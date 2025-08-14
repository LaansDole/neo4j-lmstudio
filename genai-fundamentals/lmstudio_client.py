"""
LM Studio Client Configuration

This module provides utilities for configuring and connecting to LM Studio
for local LLM and embedding model interactions.
"""

import os
from typing import List, Optional

import lmstudio as lms
from dotenv import load_dotenv
from neo4j_graphrag.embeddings.base import Embedder
from neo4j_graphrag.llm.base import LLMInterface

# Load environment variables
load_dotenv()


def get_lmstudio_llm(model_name: Optional[str] = None):
    """
    Get an LM Studio LLM model instance.

    Args:
        model_name: Optional model name. If not provided, uses default from environment

    Returns:
        LM Studio LLM model instance
    """
    if model_name is None:
        model_name = os.getenv("LMSTUDIO_CHAT_MODEL", "llama-3.2-1b-instruct")

    return lms.llm(model_name)


def get_lmstudio_embedding(model_name: Optional[str] = None):
    """
    Get an LM Studio embedding model instance.

    Args:
        model_name: Optional model name. If not provided, uses default from environment

    Returns:
        LM Studio embedding model instance
    """
    if model_name is None:
        model_name = os.getenv("LMSTUDIO_EMBEDDING_MODEL", "text-embedding-nomic-embed-text-v1.5")

    return lms.embedding_model(model_name)


class LMStudioLLM(LLMInterface):
    """
    LM Studio LLM implementation for Neo4j GraphRAG.
    """

    def __init__(self, model_instance):
        """
        Initialize with LM Studio model instance.

        Args:
            model_instance: LM Studio LLM model instance
        """
        self.model = model_instance

    def invoke(self, input: str) -> str:
        """
        Generate text completion using LM Studio LLM.

        Args:
            input: Input text prompt

        Returns:
            Generated text completion
        """
        try:
            result = self.model.complete(input)
            return result.content
        except Exception as e:
            raise RuntimeError(f"LM Studio LLM completion failed: {e}")

    async def ainvoke(self, input: str) -> str:
        """
        Async generate text completion using LM Studio LLM.

        Args:
            input: Input text prompt

        Returns:
            Generated text completion
        """
        # For now, just call the sync version since LM Studio SDK doesn't require async
        return self.invoke(input)


class LMStudioEmbedder(Embedder):
    """
    LM Studio Embedder implementation for Neo4j GraphRAG.
    """

    def __init__(self, model_instance):
        """
        Initialize with LM Studio embedding model instance.

        Args:
            model_instance: LM Studio embedding model instance
        """
        self.model = model_instance

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query text.

        Args:
            text: Input text to embed

        Returns:
            List of embedding values
        """
        try:
            embedding = self.model.embed(text)
            return embedding
        except Exception as e:
            raise RuntimeError(f"LM Studio embedding failed: {e}")


def get_chat_model():
    """
    Convenience function to get the default chat model.

    Returns:
        LM Studio LLM model instance for chat
    """
    return get_lmstudio_llm()


def get_embedding_model():
    """
    Convenience function to get the default embedding model.

    Returns:
        LM Studio embedding model instance
    """
    return get_lmstudio_embedding()
