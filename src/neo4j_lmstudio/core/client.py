"""
LMStudio Client for Neo4j Integration

This module provides the core client functionality for connecting to LMStudio
and managing model interactions within the Neo4j context using the official LMStudio SDK.
"""

import os
from typing import Optional, Dict, Any
import lmstudio as lms
from dotenv import load_dotenv


class LMStudioClient:
    """
    LMStudio client for managing connections and model operations.
    
    This class provides a centralized interface for interacting with LMStudio
    using the official LMStudio Python SDK.
    """
    
    def __init__(
        self, 
        server_host: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize LMStudio client.
        
        Args:
            server_host: LMStudio server host. Defaults to environment variable or localhost:1234
            **kwargs: Additional parameters for LMStudio configuration
        """
        load_dotenv()
        
        self.server_host = server_host or os.getenv("LMSTUDIO_API_HOST", "localhost:1234")
        
        # Configure the default LMStudio client
        lms.configure_default_client(self.server_host)
        
        # Default model configurations
        self.default_chat_model = os.getenv("LMSTUDIO_CHAT_MODEL", "meta-llama-3.1-8b-instruct")
        self.default_embedding_model = os.getenv("LMSTUDIO_EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5")
    
    def health_check(self) -> bool:
        """
        Check if LMStudio server is healthy and responsive.
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # Try to get a model to test connectivity
            model = lms.llm()
            return True
        except Exception:
            return False
    
    def list_models(self) -> Dict[str, Any]:
        """
        List available models on the LMStudio server.
        
        Returns:
            Dictionary containing model information
        """
        try:
            # Note: The official SDK doesn't have a direct list_models method
            # We'll try to create a default model and consider it successful
            model = lms.llm()
            return {
                "models": ["Available via LMStudio SDK"],
                "count": 1,
                "status": "success",
                "note": "Use lms.llm() or lms.llm('model-name') to access models"
            }
        except Exception as e:
            return {
                "models": [],
                "count": 0,
                "status": "error",
                "error": str(e)
            }
    
    def get_chat_model(self, model_name: Optional[str] = None) -> str:
        """
        Get chat model name.
        
        Args:
            model_name: Optional specific model name
            
        Returns:
            Model name to use for chat completions
        """
        return model_name or self.default_chat_model
    
    def get_llm(self, model_name: Optional[str] = None):
        """
        Get LMStudio LLM instance.
        
        Args:
            model_name: Optional specific model name
            
        Returns:
            LMStudio LLM instance
        """
        if model_name:
            return lms.llm(model_name)
        else:
            return lms.llm()
    
    def get_chat(self, system_message: Optional[str] = None):
        """
        Get LMStudio Chat instance.
        
        Args:
            system_message: Optional system message for the chat
            
        Returns:
            LMStudio Chat instance
        """
        if system_message:
            return lms.Chat(system_message)
        else:
            return lms.Chat()
    
    def respond(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Generate a response using LMStudio.
        
        Args:
            prompt: Input prompt
            model_name: Optional model name
            
        Returns:
            Generated response
        """
        model = self.get_llm(model_name)
        result = model.respond(prompt)
        
        # Handle PredictionResult object
        if hasattr(result, 'content'):
            return result.content
        else:
            return str(result)
    
    def respond_with_history(self, messages: list, model_name: Optional[str] = None) -> str:
        """
        Generate a response with message history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model_name: Optional model name
            
        Returns:
            Generated response
        """
        model = self.get_llm(model_name)
        result = model.respond({"messages": messages})
        
        # Handle PredictionResult object
        if hasattr(result, 'content'):
            return result.content
        else:
            return str(result)
    
    def get_embedding_model(self, model_name: Optional[str] = None):
        """
        Get an embedding model instance using the official SDK.
        
        Args:
            model_name: Name of the embedding model
            
        Returns:
            LMStudio embedding model instance
        """
        try:
            if model_name:
                return lms.embedding_model(model_name)
            else:
                # Use default embedding model
                return lms.embedding_model(self.default_embedding_model)
        except Exception as e:
            raise RuntimeError(f"Failed to get embedding model '{model_name}': {e}")
    
    def list_downloaded_models(self):
        """
        List downloaded models in LMStudio.
        
        Returns:
            List of downloaded models
        """
        try:
            return lms.list_downloaded_models()
        except Exception as e:
            raise RuntimeError(f"Failed to list downloaded models: {e}")
    
    def list_loaded_models(self):
        """
        List currently loaded models in LMStudio.
        
        Returns:
            List of loaded models
        """
        try:
            return lms.list_loaded_models()
        except Exception as e:
            raise RuntimeError(f"Failed to list loaded models: {e}")
    
    def validate_connection(self) -> bool:
        """
        Validate the connection to LMStudio server.
        
        Returns:
            True if connection is valid
        """
        try:
            # Try to get a simple LLM as a connection test
            test_llm = self.get_llm()
            return True
        except Exception:
            return False


# Global client instance
_client = None


def get_client() -> LMStudioClient:
    """
    Get the global LMStudio client instance.
    
    Returns:
        LMStudio client instance
    """
    global _client
    if _client is None:
        _client = LMStudioClient()
    return _client


def set_client(client: LMStudioClient):
    """
    Set the global LMStudio client instance.
    
    Args:
        client: LMStudio client instance to set as global
    """
    global _client
    _client = client
