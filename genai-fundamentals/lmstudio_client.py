import os
from typing import List, Optional

from dotenv import load_dotenv
from neo4j_graphrag.embeddings.base import Embedder
from neo4j_graphrag.llm.base import LLMInterface
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure the default LM Studio client
client = OpenAI(
    base_url=os.getenv("LMSTUDIO_API_HOST", "http://127.0.0.1:1234/v1"),
    api_key="lm-studio",
)


def get_lmstudio_llm(model_name: Optional[str] = None):
    """
    Get an LM Studio LLM model instance.

    Args:
        model_name: Optional model name. If not provided, uses default from environment

    Returns:
        LM Studio LLM model instance
    """
    if model_name is None:
        model_name = os.getenv("LMSTUDIO_CHAT_MODEL", "meta-llama-3.1-8b-instruct")

    return model_name


def get_lmstudio_embedding(model_name: Optional[str] = None):
    """
    Get an LM Studio embedding model instance.

    Args:
        model_name: Optional model name. If not provided, uses default from environment

    Returns:
        LM Studio embedding model instance
    """
    if model_name is None:
        model_name = os.getenv("LMSTUDIO_EMBEDDING_MODEL", "nomic-ai/nomic-embed-text-v1.5")

    return model_name


class LMStudioLLM(LLMInterface):
    """
    LM Studio LLM wrapper for Neo4j GraphRAG compatibility.

    This class implements the LLMInterface to enable Neo4j GraphRAG
    to work with LM Studio's local language models using OpenAI's library.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize LM Studio LLM.

        Args:
            model_name: Name of the LM Studio model to use.
                       If None, uses environment variable LMSTUDIO_CHAT_MODEL
        """
        self.model = get_lmstudio_llm(model_name)

    def invoke(self, input: str) -> str:
        """
        Generate text completion using LM Studio LLM with proper Chat API.

        Args:
            input: Input text prompt

        Returns:
            Generated text completion
        """
        try:
            messages = [{"role": "user", "content": input}]
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content
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
        # For now, just call the sync version
        return self.invoke(input)


class LMStudioEmbedder(Embedder):
    """
    LM Studio Embedder implementation for Neo4j GraphRAG.
    """

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize with LM Studio embedding model name.

        Args:
            model_name: Optional model name. If not provided, uses default from environment
        """
        self.model = get_lmstudio_embedding(model_name)

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a query text.

        Args:
            text: Input text to embed

        Returns:
            List of embedding values
        """
        try:
            response = client.embeddings.create(model=self.model, input=[text])
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"LM Studio embedding failed: {e}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_query(text))
        return embeddings


def get_chat_model(model_name: Optional[str] = None):
    """
    Convenience function to get the default chat model.

    Args:
        model_name: Optional model name

    Returns:
        LM Studio LLM model instance for chat
    """
    return get_lmstudio_llm(model_name)


def get_embedding_model(model_name: Optional[str] = None):
    """
    Convenience function to get the default embedding model.

    Args:
        model_name: Optional model name

    Returns:
        LM Studio embedding model instance
    """
    return get_lmstudio_embedding(model_name)
