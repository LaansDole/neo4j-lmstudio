"""
Vector-Cypher RAG Implementation

This module provides vector-based retrieval with custom Cypher queries
for enhanced graph traversal and data retrieval.
"""

from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.retrievers import VectorCypherRetriever

from ..core.embeddings import LMStudioEmbedder
from ..core.llm import LMStudioLLM
from ..config.settings import get_settings


class VectorCypherRAG:
    """
    Vector-Cypher Retrieval-Augmented Generation system.
    
    This class implements vector-based RAG with custom Cypher queries
    for advanced graph traversal and enriched retrieval results.
    """
    
    def __init__(
        self,
        neo4j_driver=None,
        embedder: Optional[LMStudioEmbedder] = None,
        llm: Optional[LMStudioLLM] = None,
        index_name: Optional[str] = None,
        retrieval_query: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Vector-Cypher RAG system.
        
        Args:
            neo4j_driver: Neo4j database driver
            embedder: LMStudio embedder instance
            llm: LMStudio LLM instance
            index_name: Name of the vector index in Neo4j
            retrieval_query: Custom Cypher query for retrieval
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
        
        # Initialize embedder
        self.embedder = embedder or LMStudioEmbedder()
        
        # Initialize LLM
        self.llm = llm or LMStudioLLM()
        
        # Configuration
        self.index_name = index_name or self.settings.rag.vector_index_name
        self.retrieval_query = retrieval_query or self._get_default_retrieval_query()
        
        # Initialize retriever
        self.retriever = VectorCypherRetriever(
            driver=self.driver,
            index_name=self.index_name,
            embedder=self.embedder,
            retrieval_query=self.retrieval_query,
            **kwargs
        )
        
        # Initialize GraphRAG pipeline
        self.rag_pipeline = GraphRAG(
            retriever=self.retriever,
            llm=self.llm
        )
    
    def _get_default_retrieval_query(self) -> str:
        """
        Get default Cypher retrieval query for movie recommendations.
        
        Returns:
            Default Cypher query string
        """
        return """
        MATCH (node)<-[r:RATED]-()
        RETURN 
          node.title AS title, 
          node.plot AS plot, 
          score AS similarityScore, 
          collect { MATCH (node)-[:IN_GENRE]->(g) RETURN g.name } as genres, 
          collect { MATCH (node)<-[:ACTED_IN]-(a) RETURN a.name } as actors, 
          avg(r.rating) as userRating
        ORDER BY userRating DESC
        """
    
    def search(
        self, 
        query_text: str, 
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        return_context: bool = False,
        **kwargs
    ) -> Any:
        """
        Perform vector-cypher RAG search.
        
        Args:
            query_text: Query text to search for
            top_k: Number of top results to retrieve
            similarity_threshold: Minimum similarity threshold
            return_context: Whether to return retrieval context
            **kwargs: Additional parameters
            
        Returns:
            RAG search response
        """
        # Prepare retriever configuration
        retriever_config = {
            "top_k": top_k or self.settings.rag.top_k,
            **kwargs
        }
        
        if similarity_threshold is not None:
            retriever_config["similarity_threshold"] = similarity_threshold
        
        # Perform search
        response = self.rag_pipeline.search(
            query_text=query_text,
            retriever_config=retriever_config,
            return_context=return_context
        )
        
        return response
    
    def retrieve_only(
        self, 
        query_text: str, 
        top_k: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Perform vector-cypher retrieval without generation.
        
        Args:
            query_text: Query text to search for
            top_k: Number of top results to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Retrieval results
        """
        return self.retriever.search(
            query_text=query_text,
            top_k=top_k or self.settings.rag.top_k,
            **kwargs
        )
    
    def update_retrieval_query(self, new_query: str):
        """
        Update the retrieval Cypher query.
        
        Args:
            new_query: New Cypher query string
        """
        self.retrieval_query = new_query
        self.retriever = VectorCypherRetriever(
            driver=self.driver,
            index_name=self.index_name,
            embedder=self.embedder,
            retrieval_query=self.retrieval_query
        )
        self.rag_pipeline = GraphRAG(
            retriever=self.retriever,
            llm=self.llm
        )
    
    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate the RAG system setup.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "vector_cypher_rag": True,
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
            validation_results["vector_cypher_rag"] = False
        
        # Test embedder
        try:
            self.embedder.validate_connection()
            validation_results["components"]["embedder"] = True
        except Exception as e:
            validation_results["components"]["embedder"] = False
            validation_results["errors"].append(f"Embedder validation failed: {e}")
            validation_results["vector_cypher_rag"] = False
        
        # Test LLM
        try:
            test_response = self.llm.invoke("Test")
            validation_results["components"]["llm"] = bool(test_response)
        except Exception as e:
            validation_results["components"]["llm"] = False
            validation_results["errors"].append(f"LLM validation failed: {e}")
            validation_results["vector_cypher_rag"] = False
        
        # Test vector index and Cypher query
        try:
            test_result = self.retrieve_only("test query", top_k=1)
            validation_results["components"]["vector_cypher_retrieval"] = True
        except Exception as e:
            validation_results["components"]["vector_cypher_retrieval"] = False
            validation_results["warnings"].append(f"Vector-Cypher retrieval test failed: {e}")
        
        return validation_results
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the Vector-Cypher RAG system.
        
        Returns:
            Dictionary with system information
        """
        return {
            "type": "VectorCypherRAG",
            "index_name": self.index_name,
            "retrieval_query": self.retrieval_query,
            "embedder_info": self.embedder.get_model_info(),
            "llm_info": self.llm.get_model_info(),
            "settings": {
                "top_k": self.settings.rag.top_k,
                "similarity_threshold": self.settings.rag.similarity_threshold,
                "batch_size": self.settings.rag.batch_size
            }
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
