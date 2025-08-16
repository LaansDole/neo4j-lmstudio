"""
Text-to-Cypher RAG Implementation

This module provides text-to-Cypher retrieval-augmented generation,
converting natural language queries into Cypher queries for Neo4j.
"""

from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.retrievers import Text2CypherRetriever

from ..core.llm import LMStudioLLM
from ..config.settings import get_settings


class Text2CypherRAG:
    """
    Text-to-Cypher Retrieval-Augmented Generation system.
    
    This class implements text-to-Cypher RAG that converts natural language
    queries into Cypher queries for direct graph database querying.
    """
    
    def __init__(
        self,
        neo4j_driver=None,
        llm: Optional[LMStudioLLM] = None,
        cypher_llm: Optional[LMStudioLLM] = None,
        neo4j_schema: Optional[str] = None,
        examples: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize Text-to-Cypher RAG system.
        
        Args:
            neo4j_driver: Neo4j database driver
            llm: LMStudio LLM instance for response generation
            cypher_llm: LMStudio LLM instance for Cypher generation
            neo4j_schema: Neo4j schema description for better Cypher generation
            examples: Example query pairs for few-shot learning
            **kwargs: Additional parameters
        """
        self.settings = get_settings()
        
        # Initialize Neo4j driver
        if neo4j_driver is None:
            self.driver = GraphDatabase.driver(
                self.settings.neo4j.uri,
                auth=(self.settings.neo4j.username, self.settings.neo4j.password),
                database=self.settings.neo4j.database
            )
        else:
            self.driver = neo4j_driver
        
        # Initialize LLMs
        self.llm = llm or LMStudioLLM()
        self.cypher_llm = cypher_llm or LMStudioLLM()
        
        # Configuration
        self.neo4j_schema = neo4j_schema
        self.examples = examples or []
        
        # Prepare retriever parameters
        retriever_params = {"driver": self.driver, "llm": self.cypher_llm}
        
        if self.neo4j_schema:
            retriever_params["neo4j_schema"] = self.neo4j_schema
        
        if self.examples:
            retriever_params["examples"] = self.examples
        
        retriever_params.update(kwargs)
        
        # Initialize retriever
        self.retriever = Text2CypherRetriever(**retriever_params)
        
        # Initialize GraphRAG pipeline
        self.rag_pipeline = GraphRAG(
            retriever=self.retriever,
            llm=self.llm
        )
    
    def search(
        self, 
        query_text: str, 
        return_context: bool = False,
        **kwargs
    ) -> Any:
        """
        Perform text-to-Cypher RAG search.
        
        Args:
            query_text: Natural language query text
            return_context: Whether to return retrieval context
            **kwargs: Additional parameters
            
        Returns:
            RAG search response with generated Cypher and results
        """
        # Perform search
        response = self.rag_pipeline.search(
            query_text=query_text,
            return_context=return_context,
            **kwargs
        )
        
        return response
    
    def generate_cypher(self, query_text: str) -> str:
        """
        Generate Cypher query from natural language.
        
        Args:
            query_text: Natural language query text
            
        Returns:
            Generated Cypher query string
        """
        try:
            result = self.retriever.search(query_text=query_text)
            return result.metadata.get("cypher", "")
        except Exception as e:
            raise RuntimeError(f"Cypher generation failed: {e}")
    
    def execute_cypher(self, cypher_query: str) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query directly.
        
        Args:
            cypher_query: Cypher query string to execute
            
        Returns:
            Query results as list of dictionaries
        """
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query)
                return [record.data() for record in result]
        except Exception as e:
            raise RuntimeError(f"Cypher execution failed: {e}")
    
    def add_examples(self, new_examples: List[str]):
        """
        Add new examples for few-shot learning.
        
        Args:
            new_examples: List of new example query pairs
        """
        self.examples.extend(new_examples)
        
        # Reinitialize retriever with updated examples
        retriever_params = {
            "driver": self.driver,
            "llm": self.cypher_llm,
            "examples": self.examples
        }
        
        if self.neo4j_schema:
            retriever_params["neo4j_schema"] = self.neo4j_schema
        
        self.retriever = Text2CypherRetriever(**retriever_params)
        self.rag_pipeline = GraphRAG(
            retriever=self.retriever,
            llm=self.llm
        )
    
    def update_schema(self, new_schema: str):
        """
        Update the Neo4j schema description.
        
        Args:
            new_schema: New schema description string
        """
        self.neo4j_schema = new_schema
        
        # Reinitialize retriever with updated schema
        retriever_params = {
            "driver": self.driver,
            "llm": self.cypher_llm,
            "neo4j_schema": self.neo4j_schema
        }
        
        if self.examples:
            retriever_params["examples"] = self.examples
        
        self.retriever = Text2CypherRetriever(**retriever_params)
        self.rag_pipeline = GraphRAG(
            retriever=self.retriever,
            llm=self.llm
        )
    
    def get_schema_from_database(self) -> str:
        """
        Automatically extract schema from the Neo4j database.
        
        Returns:
            Extracted schema description
        """
        try:
            with self.driver.session() as session:
                # Get node labels and their properties
                node_result = session.run("""
                CALL db.schema.nodeTypeProperties() 
                YIELD nodeType, propertyName, propertyTypes
                RETURN nodeType, collect({property: propertyName, types: propertyTypes}) as properties
                """)
                
                # Get relationship types and their properties
                rel_result = session.run("""
                CALL db.schema.relTypeProperties() 
                YIELD relType, propertyName, propertyTypes
                RETURN relType, collect({property: propertyName, types: propertyTypes}) as properties
                """)
                
                # Get relationships between nodes
                pattern_result = session.run("""
                CALL db.schema.visualization()
                YIELD nodes, relationships
                UNWIND relationships as rel
                RETURN DISTINCT rel.type as relationshipType,
                       [n IN nodes WHERE n.id = rel.start][0].labels[0] as startNode,
                       [n IN nodes WHERE n.id = rel.end][0].labels[0] as endNode
                """)
                
                # Build schema description
                schema_parts = ["Node properties:"]
                for record in node_result:
                    node_type = record["nodeType"]
                    properties = record["properties"]
                    prop_strs = [f"{p['property']}: {', '.join(p['types'])}" for p in properties]
                    schema_parts.append(f"{node_type} {{{', '.join(prop_strs)}}}")
                
                schema_parts.append("\nRelationship properties:")
                for record in rel_result:
                    rel_type = record["relType"]
                    properties = record["properties"]
                    prop_strs = [f"{p['property']}: {', '.join(p['types'])}" for p in properties]
                    schema_parts.append(f"{rel_type} {{{', '.join(prop_strs)}}}")
                
                schema_parts.append("\nThe relationships:")
                for record in pattern_result:
                    start_node = record["startNode"]
                    rel_type = record["relationshipType"]
                    end_node = record["endNode"]
                    schema_parts.append(f"(:{start_node})-[:{rel_type}]->(:{end_node})")
                
                return "\n".join(schema_parts)
                
        except Exception as e:
            raise RuntimeError(f"Schema extraction failed: {e}")
    
    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate the RAG system setup.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "text2cypher_rag": True,
            "components": {},
            "errors": [],
            "warnings": []
        }
        
        # Test Neo4j connection
        try:
            self.driver.verify_connectivity()
            validation_results["components"]["neo4j"] = True
        except Exception as e:
            validation_results["components"]["neo4j"] = False
            validation_results["errors"].append(f"Neo4j connection failed: {e}")
            validation_results["text2cypher_rag"] = False
        
        # Test Cypher LLM
        try:
            test_response = self.cypher_llm.invoke("Test")
            validation_results["components"]["cypher_llm"] = bool(test_response)
        except Exception as e:
            validation_results["components"]["cypher_llm"] = False
            validation_results["errors"].append(f"Cypher LLM validation failed: {e}")
            validation_results["text2cypher_rag"] = False
        
        # Test response LLM
        try:
            test_response = self.llm.invoke("Test")
            validation_results["components"]["response_llm"] = bool(test_response)
        except Exception as e:
            validation_results["components"]["response_llm"] = False
            validation_results["errors"].append(f"Response LLM validation failed: {e}")
            validation_results["text2cypher_rag"] = False
        
        # Test Cypher generation
        try:
            test_cypher = self.generate_cypher("What nodes exist?")
            validation_results["components"]["cypher_generation"] = bool(test_cypher)
        except Exception as e:
            validation_results["components"]["cypher_generation"] = False
            validation_results["warnings"].append(f"Cypher generation test failed: {e}")
        
        return validation_results
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the Text-to-Cypher RAG system.
        
        Returns:
            Dictionary with system information
        """
        return {
            "type": "Text2CypherRAG",
            "schema_provided": bool(self.neo4j_schema),
            "examples_count": len(self.examples),
            "cypher_llm_info": self.cypher_llm.get_model_info(),
            "response_llm_info": self.llm.get_model_info(),
        }
    
    def close(self):
        """Close the Neo4j driver connection."""
        if hasattr(self, 'driver'):
            self.driver.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
