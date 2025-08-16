#!/usr/bin/env python3
"""
System Health Check Example - Official LMStudio SDK

This example demonstrates how to check the health of all
system components in the Neo4j LMStudio integration using the official SDK.
"""

import sys
import os
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from neo4j_lmstudio.utils.helpers import HealthChecker, ConnectionManager, SchemaExtractor
from neo4j_lmstudio.config import get_settings
from neo4j_lmstudio.core.client import get_client


def print_health_result(result):
    """Print health check result in a formatted way."""
    service = result.get("service", "Unknown")
    healthy = result.get("healthy", False)
    response_time = result.get("response_time_ms")
    error = result.get("error")
    
    status_icon = "✅" if healthy else "❌"
    print(f"{status_icon} {service.upper()}")
    
    if healthy:
        if response_time is not None:
            print(f"    Response time: {response_time}ms")
        
        details = result.get("details", {})
        if details:
            for key, value in details.items():
                if isinstance(value, list) and len(value) > 3:
                    print(f"    {key}: {len(value)} items")
                else:
                    print(f"    {key}: {value}")
    else:
        print(f"    Error: {error}")
    print()


def test_official_sdk():
    """Test the official LMStudio SDK integration."""
    print("🔧 Testing Official LMStudio SDK Integration:")
    print("-" * 40)
    
    try:
        # Test client creation
        client = get_client()
        print(f"✅ LMStudio client created")
        print(f"    Server host: {client.server_host}")
        print(f"    Default chat model: {client.default_chat_model}")
        print(f"    Default embedding model: {client.default_embedding_model}")
        
        # Test connection validation
        is_connected = client.validate_connection()
        connection_status = "✅ Connected" if is_connected else "❌ Not connected"
        print(f"    Connection status: {connection_status}")
        
        # Test health check
        is_healthy = client.health_check()
        health_status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
        print(f"    Health status: {health_status}")
        
        if is_connected and is_healthy:
            # Test model listing
            try:
                downloaded_models = client.list_downloaded_models()
                print(f"    Downloaded models: {len(downloaded_models)}")
            except Exception as e:
                print(f"    Downloaded models: Error - {e}")
            
            try:
                loaded_models = client.list_loaded_models()
                print(f"    Loaded models: {len(loaded_models)}")
            except Exception as e:
                print(f"    Loaded models: Error - {e}")
        
        print()
        return is_connected and is_healthy
        
    except Exception as e:
        print(f"❌ Official SDK test failed: {e}")
        print()
        return False


def main():
    """Run health check example."""
    print("🏥 Neo4j LMStudio Health Check (Official SDK)")
    print("=" * 50)
    
    # Test official SDK first
    sdk_working = test_official_sdk()
    
    # Get settings and validate
    settings = get_settings()
    print("⚙️  Configuration Validation:")
    validation = settings.validate()
    
    if validation["valid"]:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed:")
        for error in validation["errors"]:
            print(f"  - {error}")
    
    if validation["warnings"]:
        print("⚠️  Configuration warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
    print()
    
    # Initialize health checker
    connection_manager = ConnectionManager()
    health_checker = HealthChecker(connection_manager)
    
    print("🔍 Running Individual Health Checks:")
    print("-" * 40)
    
    # Check each component individually
    try:
        # Neo4j health
        print("Checking Neo4j...")
        neo4j_result = health_checker.check_neo4j_health()
        print_health_result(neo4j_result)
        
        # LMStudio health (using official SDK)
        print("Checking LMStudio (Official SDK)...")
        lmstudio_result = health_checker.check_lmstudio_health()
        # Add SDK info to result
        if "details" not in lmstudio_result:
            lmstudio_result["details"] = {}
        lmstudio_result["details"]["using_official_sdk"] = True
        lmstudio_result["details"]["sdk_version"] = "1.3.1"
        print_health_result(lmstudio_result)
        
        # Embedder health
        print("Checking Embedder (Official SDK)...")
        embedder_result = health_checker.check_embedder_health()
        print_health_result(embedder_result)
        
        # LLM health
        print("Checking LLM (Official SDK)...")
        llm_result = health_checker.check_llm_health()
        print_health_result(llm_result)
        
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        return
    except Exception as e:
        print(f"❌ Individual health checks failed: {e}")
    
    print("🏥 Comprehensive Health Check:")
    print("-" * 40)
    
    try:
        # Run comprehensive health check
        overall_result = health_checker.check_all_health()
        
        overall_status = "✅ HEALTHY" if overall_result["overall_healthy"] else "❌ UNHEALTHY"
        print(f"Overall Status: {overall_status}")
        print(f"Timestamp: {overall_result['timestamp']}")
        print(f"Using Official SDK: ✅ Yes")
        print()
        
        # Display component details
        print("Component Details:")
        for component_name, component_result in overall_result["components"].items():
            print_health_result(component_result)
        
    except Exception as e:
        print(f"❌ Comprehensive health check failed: {e}")
    
    # Schema extraction example
    print("📋 Database Schema Information:")
    print("-" * 40)
    
    try:
        schema_extractor = SchemaExtractor(connection_manager)
        
        # Get schema summary
        schema_summary = schema_extractor.get_schema_summary()
        print("Schema Summary:")
        print(schema_summary)
        print()
        
        # Get full schema (optional, can be large)
        print("🔍 Extracting full schema...")
        full_schema = schema_extractor.extract_full_schema()
        
        print(f"Schema Statistics:")
        print(f"  Node types: {len(full_schema['nodes'])}")
        print(f"  Relationship types: {len(full_schema['relationships'])}")
        print(f"  Patterns: {len(full_schema['patterns'])}")
        print(f"  Indexes: {len(full_schema['indexes'])}")
        print(f"  Constraints: {len(full_schema['constraints'])}")
        print()
        
        # Show some example patterns
        if full_schema['patterns']:
            print("Example Relationship Patterns:")
            for pattern in full_schema['patterns'][:5]:
                print(f"  (:{pattern['start_node']})-[:{pattern['relationship']}]->(:{pattern['end_node']})")
            if len(full_schema['patterns']) > 5:
                print(f"  ... and {len(full_schema['patterns']) - 5} more")
        
    except Exception as e:
        print(f"❌ Schema extraction failed: {e}")
    
    # Configuration summary
    print("\n⚙️  Configuration Summary (Official SDK):")
    print("-" * 40)
    config_dict = settings.to_dict()
    
    print("LMStudio (Official SDK):")
    for key, value in config_dict["lmstudio"].items():
        print(f"  {key}: {value}")
    print(f"  sdk_version: 1.3.1")
    print(f"  using_official_sdk: True")
    
    print("\nNeo4j:")
    for key, value in config_dict["neo4j"].items():
        print(f"  {key}: {value}")
    
    print("\nRAG:")
    for key, value in config_dict["rag"].items():
        print(f"  {key}: {value}")
    
    # Cleanup
    try:
        connection_manager.close_connections()
        print("\n🧹 Connections closed successfully")
    except Exception as e:
        print(f"\n⚠️  Error closing connections: {e}")


if __name__ == "__main__":
    main()
