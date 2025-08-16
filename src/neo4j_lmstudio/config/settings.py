"""
Configuration Management for Neo4j LMStudio Integration

This module provides configuration management with environment variable support,
validation, and default values for the Neo4j LMStudio integration.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class LMStudioConfig:
    """LMStudio-specific configuration."""
    api_host: str = "http://127.0.0.1:1234/v1"
    api_key: str = "lm-studio"
    chat_model: str = "meta-llama-3.1-8b-instruct"
    embedding_model: str = "nomic-ai/nomic-embed-text-v1.5"
    timeout: int = 300
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class Neo4jConfig:
    """Neo4j database configuration."""
    uri: str = "neo4j://localhost:7687"
    username: str = "neo4j"
    password: str = ""
    database: str = "neo4j"
    connection_timeout: int = 30
    max_connection_lifetime: int = 3600


@dataclass
class RAGConfig:
    """RAG (Retrieval-Augmented Generation) configuration."""
    vector_index_name: str = "moviePlots"
    top_k: int = 5
    similarity_threshold: float = 0.7
    batch_size: int = 32
    return_properties: list = field(default_factory=lambda: ["title", "plot"])


@dataclass
class Settings:
    """
    Main configuration class for Neo4j LMStudio integration.
    
    This class manages all configuration settings, loads from environment
    variables, and provides validation and defaults.
    """
    lmstudio: LMStudioConfig = field(default_factory=LMStudioConfig)
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    
    debug: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Load configuration from environment variables after initialization."""
        self.load_from_env()
    
    def load_from_env(self):
        """Load configuration from environment variables."""
        load_dotenv()
        
        # LMStudio configuration
        self.lmstudio.api_host = os.getenv("LMSTUDIO_API_HOST", self.lmstudio.api_host)
        self.lmstudio.api_key = os.getenv("LMSTUDIO_API_KEY", self.lmstudio.api_key)
        self.lmstudio.chat_model = os.getenv("LMSTUDIO_CHAT_MODEL", self.lmstudio.chat_model)
        self.lmstudio.embedding_model = os.getenv("LMSTUDIO_EMBEDDING_MODEL", self.lmstudio.embedding_model)
        
        # Convert string environment variables to appropriate types
        if timeout := os.getenv("LMSTUDIO_TIMEOUT"):
            self.lmstudio.timeout = int(timeout)
        if max_retries := os.getenv("LMSTUDIO_MAX_RETRIES"):
            self.lmstudio.max_retries = int(max_retries)
        if temperature := os.getenv("LMSTUDIO_TEMPERATURE"):
            self.lmstudio.temperature = float(temperature)
        if max_tokens := os.getenv("LMSTUDIO_MAX_TOKENS"):
            self.lmstudio.max_tokens = int(max_tokens)
        
        # Neo4j configuration
        self.neo4j.uri = os.getenv("NEO4J_URI", self.neo4j.uri)
        self.neo4j.username = os.getenv("NEO4J_USERNAME", self.neo4j.username)
        self.neo4j.password = os.getenv("NEO4J_PASSWORD", self.neo4j.password)
        self.neo4j.database = os.getenv("NEO4J_DATABASE", self.neo4j.database)
        
        if connection_timeout := os.getenv("NEO4J_CONNECTION_TIMEOUT"):
            self.neo4j.connection_timeout = int(connection_timeout)
        if max_connection_lifetime := os.getenv("NEO4J_MAX_CONNECTION_LIFETIME"):
            self.neo4j.max_connection_lifetime = int(max_connection_lifetime)
        
        # RAG configuration
        self.rag.vector_index_name = os.getenv("RAG_VECTOR_INDEX_NAME", self.rag.vector_index_name)
        if top_k := os.getenv("RAG_TOP_K"):
            self.rag.top_k = int(top_k)
        if similarity_threshold := os.getenv("RAG_SIMILARITY_THRESHOLD"):
            self.rag.similarity_threshold = float(similarity_threshold)
        if batch_size := os.getenv("RAG_BATCH_SIZE"):
            self.rag.batch_size = int(batch_size)
        
        # General configuration
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate configuration settings.
        
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Validate LMStudio configuration
        if not self.lmstudio.api_host:
            errors.append("LMStudio API host is required")
        
        if not self.lmstudio.chat_model:
            errors.append("LMStudio chat model is required")
            
        if not self.lmstudio.embedding_model:
            errors.append("LMStudio embedding model is required")
        
        if self.lmstudio.temperature < 0 or self.lmstudio.temperature > 2:
            warnings.append("LMStudio temperature should be between 0 and 2")
        
        # Validate Neo4j configuration
        if not self.neo4j.uri:
            errors.append("Neo4j URI is required")
            
        if not self.neo4j.username:
            errors.append("Neo4j username is required")
            
        if not self.neo4j.password:
            warnings.append("Neo4j password is empty - this may cause authentication issues")
        
        # Validate RAG configuration
        if self.rag.top_k <= 0:
            errors.append("RAG top_k must be greater than 0")
            
        if self.rag.similarity_threshold < 0 or self.rag.similarity_threshold > 1:
            warnings.append("RAG similarity threshold should be between 0 and 1")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary.
        
        Returns:
            Dictionary representation of settings
        """
        return {
            "lmstudio": {
                "api_host": self.lmstudio.api_host,
                "api_key": "***" if self.lmstudio.api_key else None,
                "chat_model": self.lmstudio.chat_model,
                "embedding_model": self.lmstudio.embedding_model,
                "timeout": self.lmstudio.timeout,
                "max_retries": self.lmstudio.max_retries,
                "temperature": self.lmstudio.temperature,
                "max_tokens": self.lmstudio.max_tokens,
            },
            "neo4j": {
                "uri": self.neo4j.uri,
                "username": self.neo4j.username,
                "password": "***" if self.neo4j.password else None,
                "database": self.neo4j.database,
                "connection_timeout": self.neo4j.connection_timeout,
                "max_connection_lifetime": self.neo4j.max_connection_lifetime,
            },
            "rag": {
                "vector_index_name": self.rag.vector_index_name,
                "top_k": self.rag.top_k,
                "similarity_threshold": self.rag.similarity_threshold,
                "batch_size": self.rag.batch_size,
                "return_properties": self.rag.return_properties,
            },
            "debug": self.debug,
            "log_level": self.log_level,
        }


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def set_settings(settings: Settings):
    """
    Set the global settings instance.
    
    Args:
        settings: Settings instance to set as global
    """
    global _settings
    _settings = settings
