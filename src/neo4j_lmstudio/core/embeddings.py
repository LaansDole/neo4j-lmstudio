"""
LMStudio Embeddings Implementation

This module provides the embeddings interface implementation for LMStudio using the official SDK,
compatible with Neo4j GraphRAG framework.
"""

from typing import List, Optional, Dict, Any
from neo4j_graphrag.embeddings.base import Embedder
import lmstudio as lms
from .client import get_client


class LMStudioEmbedder(Embedder):
    """
    LMStudio Embedder implementation for Neo4j GraphRAG using the official SDK.
    
    This class implements the Embedder interface to enable Neo4j GraphRAG
    to use LMStudio's local embedding models.
    """
    
    def __init__(
        self, 
        model_name: Optional[str] = None,
        batch_size: int = 32,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize LMStudio embedder.
        
        Args:
            model_name: Name of the LMStudio embedding model to use
            batch_size: Number of texts to process in each batch
            max_retries: Maximum number of retry attempts
            **kwargs: Additional parameters
        """
        self.client = get_client()
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.additional_params = kwargs
        
        # Get the embedding model instance using official SDK
        self.embedding_model = self.client.get_embedding_model(model_name)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text using official SDK.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
            
        Raises:
            RuntimeError: If embedding generation fails
        """
        try:
            # Use official SDK embedding method
            embedding = self.embedding_model.embed(text)
            return embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            
        except Exception as e:
            raise RuntimeError(f"LMStudio embedding failed for query: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents using official SDK.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            RuntimeError: If embedding generation fails
        """
        if not texts:
            return []
        
        try:
            # Process in batches for efficiency
            embeddings = []
            
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                
                # Try to use batch embedding if available
                try:
                    batch_embeddings = self.embedding_model.embed_batch(batch)
                    if hasattr(batch_embeddings, 'tolist'):
                        embeddings.extend([emb.tolist() for emb in batch_embeddings])
                    else:
                        embeddings.extend(batch_embeddings)
                except AttributeError:
                    # Fallback to individual embeddings if batch not supported
                    for text in batch:
                        embedding = self.embedding_model.embed(text)
                        if hasattr(embedding, 'tolist'):
                            embeddings.append(embedding.tolist())
                        else:
                            embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            raise RuntimeError(f"LMStudio embedding failed for documents: {e}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text (alias for embed_query).
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        return self.embed_query(text)
    
    def get_embedding_dimensions(self) -> Optional[int]:
        """
        Get the dimensions of the embedding vectors.
        
        Returns:
            Number of dimensions, or None if unknown
        """
        try:
            # Test with a small text to get dimensions
            test_embedding = self.embed_query("test")
            return len(test_embedding)
        except Exception:
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current embedding model.
        
        Returns:
            Dictionary containing model information
        """
        try:
            # Try to get model info from the embedding model instance
            model_info = self.embedding_model.info() if hasattr(self.embedding_model, 'info') else {}
        except:
            model_info = {}
            
        return {
            "model_name": self.model_name,
            "batch_size": self.batch_size,
            "max_retries": self.max_retries,
            "dimensions": self.get_embedding_dimensions(),
            "provider": "LMStudio",
            "sdk_version": "1.3.1",
            "using_official_sdk": True,
            **model_info
        }
    
    def validate_connection(self) -> bool:
        """
        Validate that the embedding model is accessible.
        
        Returns:
            True if model is accessible, False otherwise
        """
        try:
            self.embed_query("test connection")
            return True
        except Exception:
            return False
    
    def list_available_models(self) -> List[str]:
        """
        List available embedding models in LMStudio.
        
        Returns:
            List of available embedding model names
        """
        try:
            # Use official SDK to list models
            models = lms.list_downloaded_models()
            # Filter for embedding models
            embedding_models = [
                model.identifier for model in models 
                if hasattr(model, 'type') and 'embedding' in str(model.type).lower()
            ]
            return embedding_models
        except Exception:
            return []
