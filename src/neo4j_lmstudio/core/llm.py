"""
LMStudio Language Model Implementation

This module provides the LLM interface implementation for LMStudio using the official SDK,
compatible with Neo4j GraphRAG framework.
"""

from typing import Optional, Dict, Any, Union, List
from neo4j_graphrag.llm.base import LLMInterface
from neo4j_graphrag.message_history import MessageHistory
from neo4j_graphrag.types import LLMMessage
import lmstudio as lms
from .client import get_client


class LMStudioLLM(LLMInterface):
    """
    LMStudio Language Model implementation for Neo4j GraphRAG using the official SDK.
    
    This class implements the LLMInterface to enable Neo4j GraphRAG
    to work with LMStudio's local language models using the official SDK.
    """
    
    def __init__(
        self, 
        model_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize LMStudio LLM.
        
        Args:
            model_name: Name of the LMStudio model to use
            **kwargs: Additional parameters (for compatibility)
        """
        super().__init__(model_name or "", **kwargs)
        self.client = get_client()
        self.model_name = model_name
        
        # Get the LMStudio model instance
        self.llm = self.client.get_llm(model_name)
    
    def invoke(self, input_text: str, message_history: Optional[Union[List[LLMMessage], MessageHistory]] = None, system_instruction: Optional[str] = None) -> str:
        """
        Generate text completion using LMStudio LLM.
        
        Args:
            input_text: Input text prompt
            message_history: Optional message history (for compatibility with LLMInterface)
            system_instruction: Optional system instruction (for compatibility with LLMInterface)
            
        Returns:
            Generated text completion
            
        Raises:
            RuntimeError: If LMStudio LLM completion fails
        """
        try:
            # If we have message history or system instruction, build proper messages
            if message_history or system_instruction:
                messages = []
                
                # Add system instruction if provided
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                
                # Add message history if provided
                if message_history:
                    if isinstance(message_history, MessageHistory):
                        # Convert MessageHistory to list of dicts
                        for msg in message_history.messages:
                            if hasattr(msg, 'role') and hasattr(msg, 'content'):
                                messages.append({"role": msg.role, "content": msg.content})
                    elif isinstance(message_history, list):
                        # Convert LLMMessage objects to dicts
                        for msg in message_history:
                            if hasattr(msg, 'role') and hasattr(msg, 'content'):
                                messages.append({"role": msg.role, "content": msg.content})
                            elif isinstance(msg, dict):
                                messages.append(msg)
                
                # Add the current user input
                messages.append({"role": "user", "content": input_text})
                
                # Use message history format
                response = self.client.respond_with_history(messages, self.model_name)
            else:
                # Simple prompt
                response = self.client.respond(input_text, self.model_name)
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"LMStudio LLM completion failed: {e}")
    
    async def ainvoke(self, input_text: str, message_history: Optional[Union[List[LLMMessage], MessageHistory]] = None, system_instruction: Optional[str] = None) -> str:
        """
        Async generate text completion using LMStudio LLM.
        
        Args:
            input_text: Input text prompt
            message_history: Optional message history
            system_instruction: Optional system instruction
            
        Returns:
            Generated text completion
        """
        # For now, just call the sync version
        # TODO: Implement proper async support when available in LMStudio SDK
        return self.invoke(input_text, message_history, system_instruction)
    
    def stream(self, input_text: str, chat_instance = None):
        """
        Stream text completion using LMStudio LLM.
        
        Args:
            input_text: Input text prompt
            chat_instance: Optional chat instance for multi-turn conversations
            
        Yields:
            Streaming text completion chunks
        """
        try:
            if chat_instance:
                # Use chat instance for streaming
                chat_instance.add_user_message(input_text)
                prediction_stream = self.llm.respond_stream(
                    chat_instance,
                    on_message=chat_instance.append,
                )
                for fragment in prediction_stream:
                    yield fragment.content
            else:
                # Simple streaming (if supported)
                # Note: The official SDK might not support simple streaming
                # This is a fallback approach
                response = self.client.respond(input_text, self.model_name)
                yield response
                    
        except Exception as e:
            raise RuntimeError(f"LMStudio LLM streaming failed: {e}")
    
    def create_chat_session(self, system_message: Optional[str] = None):
        """
        Create a new chat session for multi-turn conversations.
        
        Args:
            system_message: Optional system message
            
        Returns:
            Chat session instance
        """
        return self.client.get_chat(system_message)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "model_name": self.client.get_chat_model(self.model_name),
            "provider": "LMStudio",
            "sdk_version": "1.3.1",
            "using_official_sdk": True
        }
    
    def validate_connection(self) -> bool:
        """
        Validate that the LMStudio connection is working.
        
        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try a simple test
            test_response = self.invoke("Hello")
            return bool(test_response)
        except Exception:
            return False
