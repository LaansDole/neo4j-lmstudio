"""
Neo4j LMStudio Integration Package

A production-ready package for integrating Neo4j graph databases with LMStudio 
local language models, providing powerful RAG (Retrieval-Augmented Generation) 
capabilities for knowledge graphs.

This package provides:
- LMStudio integration for local language models
- Neo4j graph database connectivity
- Vector-based retrieval systems
- Text-to-Cypher query generation
- Hybrid vector-cypher retrieval
- RAG pipeline implementations
"""

from .core.client import LMStudioClient
from .core.embeddings import LMStudioEmbedder
from .core.llm import LMStudioLLM
from .rag.vector_rag import VectorRAG
from .rag.vector_cypher_rag import VectorCypherRAG
from .rag.text2cypher_rag import Text2CypherRAG
from .config.settings import Settings

__version__ = "1.0.0"
__author__ = "Neo4j LMStudio Team"
__email__ = "contact@example.com"

__all__ = [
    # Core components
    "LMStudioClient",
    "LMStudioEmbedder", 
    "LMStudioLLM",
    
    # RAG implementations
    "VectorRAG",
    "VectorCypherRAG", 
    "Text2CypherRAG",
    
    # Configuration
    "Settings",
]
