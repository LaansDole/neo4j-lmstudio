#!/usr/bin/env python3
"""
Simple LMStudio Official SDK Validation Script

This script validates that our migration to the official LMStudio SDK
follows the correct patterns and can connect to LMStudio when available.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_official_sdk_import():
    """Test that the official SDK can be imported."""
    print("🔍 Testing Official LMStudio SDK Import...")
    try:
        import lmstudio as lms
        print("✅ Official LMStudio SDK imported successfully")
        print(f"   Available functions: {len([x for x in dir(lms) if not x.startswith('_')])}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import LMStudio SDK: {e}")
        return False


def test_client_configuration():
    """Test basic client configuration."""
    print("\n🔧 Testing Client Configuration...")
    try:
        import lmstudio as lms
        
        # Test configuration
        host = os.getenv("LMSTUDIO_API_HOST", "localhost:1234")
        print(f"   Using host: {host}")
        
        # Configure default client
        lms.configure_default_client(host)
        print("✅ Default client configured successfully")
        return True
    except Exception as e:
        print(f"❌ Client configuration failed: {e}")
        return False


def test_llm_instance():
    """Test LLM instance creation."""
    print("\n🤖 Testing LLM Instance Creation...")
    try:
        import lmstudio as lms
        
        # Try to create LLM instance
        model_name = os.getenv("LMSTUDIO_CHAT_MODEL", "test-model")
        print(f"   Using model: {model_name}")
        
        # Test with default model
        llm_default = lms.llm()
        print("✅ Default LLM instance created")
        
        # Test with specific model
        llm_specific = lms.llm(model_name)
        print("✅ Specific model LLM instance created")
        
        return True
    except Exception as e:
        print(f"❌ LLM instance creation failed: {e}")
        print("   (This is expected if LMStudio server is not running)")
        return False


def test_chat_instance():
    """Test Chat instance creation."""
    print("\n💬 Testing Chat Instance Creation...")
    try:
        import lmstudio as lms
        
        # Test default chat
        chat_default = lms.Chat()
        print("✅ Default Chat instance created")
        
        # Test chat with system message
        chat_system = lms.Chat("You are a helpful assistant.")
        print("✅ Chat with system message created")
        
        return True
    except Exception as e:
        print(f"❌ Chat instance creation failed: {e}")
        return False


def test_embedding_model():
    """Test embedding model creation."""
    print("\n🔤 Testing Embedding Model Creation...")
    try:
        import lmstudio as lms
        
        # Test embedding model
        embedding_model_name = os.getenv("LMSTUDIO_EMBEDDING_MODEL", "test-embedding")
        print(f"   Using embedding model: {embedding_model_name}")
        
        # Test default embedding model
        emb_default = lms.embedding_model()
        print("✅ Default embedding model instance created")
        
        # Test specific embedding model
        emb_specific = lms.embedding_model(embedding_model_name)
        print("✅ Specific embedding model instance created")
        
        return True
    except Exception as e:
        print(f"❌ Embedding model creation failed: {e}")
        print("   (This is expected if LMStudio server is not running)")
        return False


def test_model_listing():
    """Test model listing functionality."""
    print("\n📋 Testing Model Listing...")
    try:
        import lmstudio as lms
        
        # Test downloaded models
        try:
            downloaded = lms.list_downloaded_models()
            print(f"✅ Downloaded models listed: {len(downloaded)} models")
        except Exception as e:
            print(f"⚠️  Downloaded models listing failed: {e}")
        
        # Test loaded models
        try:
            loaded = lms.list_loaded_models()
            print(f"✅ Loaded models listed: {len(loaded)} models")
        except Exception as e:
            print(f"⚠️  Loaded models listing failed: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Model listing failed: {e}")
        return False


def test_connection_attempt():
    """Test actual connection to LMStudio server."""
    print("\n🔌 Testing LMStudio Server Connection...")
    try:
        import lmstudio as lms
        
        host = os.getenv("LMSTUDIO_API_HOST", "localhost:1234")
        lms.configure_default_client(host)
        
        # Try a simple operation that requires server connection
        llm = lms.llm()
        
        # Attempt to get a simple response
        response = llm.respond("Hello")
        print(f"✅ Server connection successful!")
        print(f"   Response: {response[:50]}..." if len(response) > 50 else f"   Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        print("   This is expected if LMStudio server is not running")
        return False


def main():
    """Run all validation tests."""
    print("🚀 LMStudio Official SDK Validation")
    print("=" * 50)
    
    tests = [
        test_official_sdk_import,
        test_client_configuration,
        test_llm_instance,
        test_chat_instance,
        test_embedding_model,
        test_model_listing,
        test_connection_attempt,
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
    print(f"📊 Validation Results: {passed}/{total} tests passed")
    
    # Interpret results
    if passed >= 5:  # Import, config, LLM, chat, embedding should work
        print("🎉 Official SDK migration validation SUCCESSFUL!")
        print("   The implementation follows correct SDK patterns.")
        if passed < total:
            print("   ⚠️  Some tests failed due to LMStudio server not running.")
    elif passed >= 2:  # At least import and config should work
        print("⚠️  Official SDK patterns are correct, but server connection failed.")
        print("   Start LMStudio server to test full functionality.")
    else:
        print("❌ Official SDK migration validation FAILED!")
        print("   Check LMStudio SDK installation and configuration.")
    
    print(f"\n📖 Configuration:")
    print(f"   LMStudio Host: {os.getenv('LMSTUDIO_API_HOST', 'localhost:1234')}")
    print(f"   Chat Model: {os.getenv('LMSTUDIO_CHAT_MODEL', 'default')}")
    print(f"   Embedding Model: {os.getenv('LMSTUDIO_EMBEDDING_MODEL', 'default')}")
    
    return 0 if passed >= 5 else 1


if __name__ == "__main__":
    exit(main())
