"""
Connection and Health Management Utilities

This module provides utilities for managing connections and health checks
for Neo4j and LMStudio components.
"""

import time
from typing import Dict, Any, Optional, List
from neo4j import GraphDatabase
from ..core.client import get_client
from ..config.settings import get_settings


class ConnectionManager:
    """
    Manages connections to Neo4j and LMStudio.
    
    Provides connection pooling, retry logic, and health monitoring.
    """
    
    def __init__(self):
        """Initialize connection manager."""
        self.settings = get_settings()
        self._neo4j_driver = None
        self._lmstudio_client = None
    
    def get_neo4j_driver(self):
        """
        Get Neo4j driver with connection pooling.
        
        Returns:
            Neo4j driver instance
        """
        if self._neo4j_driver is None:
            self._neo4j_driver = GraphDatabase.driver(
                self.settings.neo4j.uri,
                auth=(self.settings.neo4j.username, self.settings.neo4j.password),
                database=self.settings.neo4j.database,
                connection_timeout=self.settings.neo4j.connection_timeout,
                max_connection_lifetime=self.settings.neo4j.max_connection_lifetime
            )
        return self._neo4j_driver
    
    def get_lmstudio_client(self):
        """
        Get LMStudio client instance.
        
        Returns:
            LMStudio client instance
        """
        if self._lmstudio_client is None:
            self._lmstudio_client = get_client()
        return self._lmstudio_client
    
    def close_connections(self):
        """Close all open connections."""
        if self._neo4j_driver:
            self._neo4j_driver.close()
            self._neo4j_driver = None
        
        # LMStudio client doesn't need explicit closing
        self._lmstudio_client = None


class HealthChecker:
    """
    Provides health checking capabilities for system components.
    """
    
    def __init__(self, connection_manager: Optional[ConnectionManager] = None):
        """
        Initialize health checker.
        
        Args:
            connection_manager: Optional connection manager instance
        """
        self.connection_manager = connection_manager or ConnectionManager()
        self.settings = get_settings()
    
    def check_neo4j_health(self) -> Dict[str, Any]:
        """
        Check Neo4j database health.
        
        Returns:
            Dictionary with health check results
        """
        result = {
            "service": "neo4j",
            "healthy": False,
            "response_time_ms": None,
            "error": None,
            "details": {}
        }
        
        try:
            start_time = time.time()
            driver = self.connection_manager.get_neo4j_driver()
            
            # Test connectivity
            driver.verify_connectivity()
            
            # Test basic query
            with driver.session() as session:
                session.run("RETURN 1 as test").single()
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            result.update({
                "healthy": True,
                "response_time_ms": round(response_time, 2),
                "details": {
                    "uri": self.settings.neo4j.uri,
                    "database": self.settings.neo4j.database,
                    "username": self.settings.neo4j.username
                }
            })
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_lmstudio_health(self) -> Dict[str, Any]:
        """
        Check LMStudio server health.
        
        Returns:
            Dictionary with health check results
        """
        result = {
            "service": "lmstudio",
            "healthy": False,
            "response_time_ms": None,
            "error": None,
            "details": {}
        }
        
        try:
            start_time = time.time()
            client = self.connection_manager.get_lmstudio_client()
            
            # Test basic health check
            is_healthy = client.health_check()
            
            if is_healthy:
                # Get model information
                models_info = client.list_models()
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                result.update({
                    "healthy": True,
                    "response_time_ms": round(response_time, 2),
                    "details": {
                        "api_host": self.settings.lmstudio.api_host,
                        "chat_model": self.settings.lmstudio.chat_model,
                        "embedding_model": self.settings.lmstudio.embedding_model,
                        "available_models": models_info.get("models", []),
                        "model_count": models_info.get("count", 0)
                    }
                })
            else:
                result["error"] = "LMStudio health check failed"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_embedder_health(self) -> Dict[str, Any]:
        """
        Check embedder functionality.
        
        Returns:
            Dictionary with health check results
        """
        result = {
            "service": "embedder",
            "healthy": False,
            "response_time_ms": None,
            "error": None,
            "details": {}
        }
        
        try:
            from ..core.embeddings import LMStudioEmbedder
            
            start_time = time.time()
            embedder = LMStudioEmbedder()
            
            # Test embedding generation
            test_embedding = embedder.embed_query("test")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            result.update({
                "healthy": True,
                "response_time_ms": round(response_time, 2),
                "details": {
                    "model": self.settings.lmstudio.embedding_model,
                    "embedding_dimensions": len(test_embedding) if test_embedding else None,
                    "test_embedding_length": len(test_embedding) if test_embedding else 0
                }
            })
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_llm_health(self) -> Dict[str, Any]:
        """
        Check LLM functionality.
        
        Returns:
            Dictionary with health check results
        """
        result = {
            "service": "llm",
            "healthy": False,
            "response_time_ms": None,
            "error": None,
            "details": {}
        }
        
        try:
            from ..core.llm import LMStudioLLM
            
            start_time = time.time()
            llm = LMStudioLLM()
            
            # Test text generation
            test_response = llm.invoke("Say 'Hello' in exactly one word.")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            result.update({
                "healthy": True,
                "response_time_ms": round(response_time, 2),
                "details": {
                    "model": self.settings.lmstudio.chat_model,
                    "test_response": test_response[:100] if test_response else None,
                    "response_length": len(test_response) if test_response else 0
                }
            })
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_all_health(self) -> Dict[str, Any]:
        """
        Check health of all system components.
        
        Returns:
            Dictionary with comprehensive health check results
        """
        results = {
            "overall_healthy": True,
            "timestamp": time.time(),
            "components": {}
        }
        
        # Check each component
        health_checks = [
            ("neo4j", self.check_neo4j_health),
            ("lmstudio", self.check_lmstudio_health),
            ("embedder", self.check_embedder_health),
            ("llm", self.check_llm_health)
        ]
        
        for component_name, health_check_func in health_checks:
            try:
                component_result = health_check_func()
                results["components"][component_name] = component_result
                
                if not component_result["healthy"]:
                    results["overall_healthy"] = False
                    
            except Exception as e:
                results["components"][component_name] = {
                    "service": component_name,
                    "healthy": False,
                    "error": f"Health check failed: {e}"
                }
                results["overall_healthy"] = False
        
        return results


class SchemaExtractor:
    """
    Extracts and manages Neo4j database schema information.
    """
    
    def __init__(self, connection_manager: Optional[ConnectionManager] = None):
        """
        Initialize schema extractor.
        
        Args:
            connection_manager: Optional connection manager instance
        """
        self.connection_manager = connection_manager or ConnectionManager()
    
    def extract_full_schema(self) -> Dict[str, Any]:
        """
        Extract comprehensive schema information from Neo4j.
        
        Returns:
            Dictionary with complete schema information
        """
        schema_info = {
            "nodes": {},
            "relationships": {},
            "patterns": [],
            "indexes": [],
            "constraints": []
        }
        
        try:
            driver = self.connection_manager.get_neo4j_driver()
            
            with driver.session() as session:
                # Get node types and properties
                node_result = session.run("""
                CALL db.schema.nodeTypeProperties() 
                YIELD nodeType, propertyName, propertyTypes
                RETURN nodeType, collect({property: propertyName, types: propertyTypes}) as properties
                """)
                
                for record in node_result:
                    node_type = record["nodeType"]
                    properties = record["properties"]
                    schema_info["nodes"][node_type] = {
                        "properties": {prop["property"]: prop["types"] for prop in properties}
                    }
                
                # Get relationship types and properties
                rel_result = session.run("""
                CALL db.schema.relTypeProperties() 
                YIELD relType, propertyName, propertyTypes
                RETURN relType, collect({property: propertyName, types: propertyTypes}) as properties
                """)
                
                for record in rel_result:
                    rel_type = record["relType"]
                    properties = record["properties"]
                    schema_info["relationships"][rel_type] = {
                        "properties": {prop["property"]: prop["types"] for prop in properties}
                    }
                
                # Get relationship patterns
                pattern_result = session.run("""
                CALL db.schema.visualization()
                YIELD nodes, relationships
                UNWIND relationships as rel
                RETURN DISTINCT rel.type as relationshipType,
                       [n IN nodes WHERE n.id = rel.start][0].labels[0] as startNode,
                       [n IN nodes WHERE n.id = rel.end][0].labels[0] as endNode
                """)
                
                for record in pattern_result:
                    pattern = {
                        "start_node": record["startNode"],
                        "relationship": record["relationshipType"],
                        "end_node": record["endNode"]
                    }
                    schema_info["patterns"].append(pattern)
                
                # Get indexes
                try:
                    index_result = session.run("SHOW INDEXES")
                    for record in index_result:
                        index_info = {
                            "name": record.get("name"),
                            "type": record.get("type"),
                            "labels": record.get("labelsOrTypes"),
                            "properties": record.get("properties"),
                            "state": record.get("state")
                        }
                        schema_info["indexes"].append(index_info)
                except Exception:
                    # Fallback for older Neo4j versions
                    pass
                
                # Get constraints
                try:
                    constraint_result = session.run("SHOW CONSTRAINTS")
                    for record in constraint_result:
                        constraint_info = {
                            "name": record.get("name"),
                            "type": record.get("type"),
                            "labels": record.get("labelsOrTypes"),
                            "properties": record.get("properties")
                        }
                        schema_info["constraints"].append(constraint_info)
                except Exception:
                    # Fallback for older Neo4j versions
                    pass
                
        except Exception as e:
            raise RuntimeError(f"Schema extraction failed: {e}")
        
        return schema_info
    
    def get_schema_summary(self) -> str:
        """
        Get a text summary of the database schema.
        
        Returns:
            Human-readable schema summary string
        """
        try:
            schema = self.extract_full_schema()
            
            summary_parts = []
            
            # Node types
            if schema["nodes"]:
                summary_parts.append("Node Types:")
                for node_type, info in schema["nodes"].items():
                    props = list(info["properties"].keys())
                    summary_parts.append(f"  {node_type}: {', '.join(props) if props else 'no properties'}")
            
            # Relationship types
            if schema["relationships"]:
                summary_parts.append("\nRelationship Types:")
                for rel_type, info in schema["relationships"].items():
                    props = list(info["properties"].keys())
                    summary_parts.append(f"  {rel_type}: {', '.join(props) if props else 'no properties'}")
            
            # Patterns
            if schema["patterns"]:
                summary_parts.append("\nRelationship Patterns:")
                for pattern in schema["patterns"]:
                    summary_parts.append(
                        f"  (:{pattern['start_node']})-[:{pattern['relationship']}]->(:{pattern['end_node']})"
                    )
            
            # Indexes
            if schema["indexes"]:
                summary_parts.append(f"\nIndexes: {len(schema['indexes'])} total")
            
            # Constraints
            if schema["constraints"]:
                summary_parts.append(f"Constraints: {len(schema['constraints'])} total")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"Schema extraction failed: {e}"
