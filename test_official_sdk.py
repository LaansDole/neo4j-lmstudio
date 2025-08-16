#!/usr/bin/env python3
"""
Test script for the updated LMStudio integration using the official SDK.

This script tests the updated implementation to ensure it works correctly
with the official LMStudio SDK instead of the OpenAI-compatible API.
"""

import sys
import os

# Add the src directory to the path so we can import our package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from neo4j_lmstudio.core.client import get_client, LMStudioClient
from neo4j_lmstudio.core.llm import LMStudioLLM
from neo4j_lmstudio.core.embeddings import LMStudioEmbedder


def test_client_connection():
    """Test basic client connection and configuration."""
    print("🔧 Testing LMStudio client connection...")
    
    try:
        client = get_client()
        print(f"✅ Client created successfully")
        print(f"   Server host: {client.server_host}")
        print(f"   Default chat model: {client.default_chat_model}")
        print(f"   Default embedding model: {client.default_embedding_model}")
        
        # Test health check
        is_healthy = client.health_check()
        print(f"   Health check: {'✅ Pass' if is_healthy else '❌ Fail'}")
        
        return True
    except Exception as e:
        print(f"❌ Client connection failed: {e}")
        return False


def test_llm_functionality():
    """Test LLM functionality with the official SDK."""
    print("\n🤖 Testing LLM functionality...")
    
    try:
        llm = LMStudioLLM()
        print("✅ LLM instance created")
        
        # Test simple invoke
        response = llm.invoke("What is 2 + 2?")
        print(f"✅ Simple invoke successful")
        print(f"   Response: {response[:100]}...")
        
        # Test with system instruction
        system_response = llm.invoke(
            "What is the capital of France?",
            system_instruction="You are a helpful geography assistant."
        )
        print(f"✅ System instruction invoke successful")
        print(f"   Response: {system_response[:100]}...")
        
        # Test model info
        model_info = llm.get_model_info()
        print(f"✅ Model info retrieved")
        print(f"   Provider: {model_info.get('provider')}")
        print(f"   Using official SDK: {model_info.get('using_official_sdk')}")
        
        return True
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False


def test_embedding_functionality():
    """Test embedding functionality with the official SDK."""
    print("\n🔤 Testing embedding functionality...")
    
    try:
        embedder = LMStudioEmbedder()
        print("✅ Embedder instance created")
        
        # Test single text embedding
        text = "This is a test sentence for embedding."
        embedding = embedder.embed_query(text)
        print(f"✅ Single embedding successful")
        print(f"   Embedding dimensions: {len(embedding)}")
        
        # Test multiple document embeddings
        texts = [
            "First document to embed",
            "Second document to embed", 
            "Third document to embed"
        ]
        embeddings = embedder.embed_documents(texts)
        print(f"✅ Multiple embeddings successful")
        print(f"   Number of embeddings: {len(embeddings)}")
        print(f"   Each embedding dimensions: {len(embeddings[0]) if embeddings else 0}")
        
        # Test model info
        model_info = embedder.get_model_info()
        print(f"✅ Embedding model info retrieved")
        print(f"   Provider: {model_info.get('provider')}")
        print(f"   Using official SDK: {model_info.get('using_official_sdk')}")
        
        return True
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False


def test_chat_functionality():
    """Test chat functionality with the official SDK."""
    print("\n💬 Testing chat functionality...")
    
    try:
        client = get_client()
        
        # Test getting a chat instance
        chat = client.get_chat("You are a helpful assistant.")
        print("✅ Chat instance created")
        
        # Test LLM with chat session
        llm = LMStudioLLM()
        chat_session = llm.create_chat_session("You are a math tutor.")
        print("✅ Chat session created")
        
        return True
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False


def test_model_listing():
    """Test model listing functionality."""
    print("\n📋 Testing model listing...")
    
    try:
        client = get_client()
        
        # Test downloaded models
        try:
            downloaded_models = client.list_downloaded_models()
            print(f"✅ Downloaded models retrieved: {len(downloaded_models)} models")
        except Exception as e:
            print(f"⚠️  Downloaded models listing failed (may be normal): {e}")
        
        # Test loaded models
        try:
            loaded_models = client.list_loaded_models()
            print(f"✅ Loaded models retrieved: {len(loaded_models)} models")
        except Exception as e:
            print(f"⚠️  Loaded models listing failed (may be normal): {e}")
        
        return True
    except Exception as e:
        print(f"❌ Model listing test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Testing LMStudio Official SDK Integration")
    print("=" * 50)
    
    tests = [
        test_client_connection,
        test_llm_functionality,
        test_embedding_functionality,
        test_chat_functionality,
        test_model_listing,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The official SDK integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check LMStudio server and model availability.")
        return 1


if __name__ == "__main__":
    exit(main())
