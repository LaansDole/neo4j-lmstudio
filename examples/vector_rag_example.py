#!/usr/bin/env python3
"""
Vector RAG Example

This example demonstrates how to use the Vector RAG system
for movie recommendations using Neo4j and LMStudio.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from neo4j_lmstudio import VectorRAG
from neo4j_lmstudio.config import get_settings


def main():
    """Run Vector RAG example."""
    print("🎬 Vector RAG Movie Recommendation Example")
    print("=" * 50)
    
    # Get settings and validate
    settings = get_settings()
    validation = settings.validate()
    
    if not validation["valid"]:
        print("❌ Configuration validation failed:")
        for error in validation["errors"]:
            print(f"  - {error}")
        return
    
    if validation["warnings"]:
        print("⚠️  Configuration warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
        print()
    
    try:
        # Initialize Vector RAG system
        print("🔧 Initializing Vector RAG system...")
        with VectorRAG() as rag:
            
            # Validate setup
            print("🔍 Validating system setup...")
            validation_result = rag.validate_setup()
            
            if not validation_result["vector_rag"]:
                print("❌ System validation failed:")
                for error in validation_result["errors"]:
                    print(f"  - {error}")
                return
            
            if validation_result["warnings"]:
                print("⚠️  System warnings:")
                for warning in validation_result["warnings"]:
                    print(f"  - {warning}")
            
            print("✅ Vector RAG system ready!")
            print()
            
            # Display system information
            info = rag.get_info()
            print("📊 System Information:")
            print(f"  Type: {info['type']}")
            print(f"  Index: {info['index_name']}")
            print(f"  LLM Model: {info['llm_info']['model_name']}")
            print(f"  Embedding Model: {info['embedder_info']['model_name']}")
            print()
            
            # Example queries
            queries = [
                "Find me movies about toys coming alive",
                "What are some good sci-fi movies about space travel?",
                "Show me animated movies with talking animals"
            ]
            
            for i, query in enumerate(queries, 1):
                print(f"🔍 Query {i}: {query}")
                print("-" * 40)
                
                try:
                    # Perform search with context
                    response = rag.search(
                        query_text=query,
                        top_k=3,
                        return_context=True
                    )
                    
                    print("🤖 AI Response:")
                    print(response.answer)
                    print()
                    
                    print("📚 Retrieved Context:")
                    for j, item in enumerate(response.retriever_result.items, 1):
                        print(f"  {j}. {item.content}")
                        score = item.metadata.get("score", "N/A")
                        print(f"     Similarity: {score}")
                    print()
                    
                except Exception as e:
                    print(f"❌ Query failed: {e}")
                    print()
            
            # Demonstrate retrieval-only functionality
            print("🔍 Testing retrieval-only mode...")
            retrieval_result = rag.retrieve_only(
                query_text="movies about friendship",
                top_k=2
            )
            
            print("📚 Retrieval Results:")
            for i, item in enumerate(retrieval_result.items, 1):
                print(f"  {i}. {item.content}")
                score = item.metadata.get("score", "N/A")
                print(f"     Similarity: {score}")
            print()
    
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        if settings.debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
