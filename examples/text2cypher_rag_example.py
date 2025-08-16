#!/usr/bin/env python3
"""
Text-to-Cypher RAG Example

This example demonstrates how to use the Text-to-Cypher RAG system
for natural language queries to Neo4j using LMStudio.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from neo4j_lmstudio import Text2CypherRAG
from neo4j_lmstudio.config import get_settings


def main():
    """Run Text-to-Cypher RAG example."""
    print("🔍 Text-to-Cypher RAG Example")
    print("=" * 40)
    
    # Get settings and validate
    settings = get_settings()
    validation = settings.validate()
    
    if not validation["valid"]:
        print("❌ Configuration validation failed:")
        for error in validation["errors"]:
            print(f"  - {error}")
        return
    
    try:
        # Example schema for better Cypher generation
        neo4j_schema = """
        Node properties:
        Person {name: STRING, born: INTEGER}
        Movie {tagline: STRING, title: STRING, released: INTEGER}
        Genre {name: STRING}
        User {name: STRING}

        Relationship properties:
        ACTED_IN {role: STRING}
        RATED {rating: INTEGER}

        The relationships:
        (:Person)-[:ACTED_IN]->(:Movie)
        (:Person)-[:DIRECTED]->(:Movie)
        (:User)-[:RATED]->(:Movie)
        (:Movie)-[:IN_GENRE]->(:Genre)
        """
        
        # Example queries for few-shot learning
        examples = [
            "USER INPUT: 'Get user ratings for a movie?' "
            "QUERY: MATCH (u:User)-[r:RATED]->(m:Movie) WHERE m.title = 'Movie Title' RETURN r.rating",
            
            "USER INPUT: 'Which actors starred in movies?' "
            "QUERY: MATCH (p:Person)-[r:ACTED_IN]->(m:Movie) RETURN p.name, m.title, r.role",
            
            "USER INPUT: 'What genres are available?' "
            "QUERY: MATCH (g:Genre) RETURN g.name"
        ]
        
        # Initialize Text-to-Cypher RAG system
        print("🔧 Initializing Text-to-Cypher RAG system...")
        with Text2CypherRAG(neo4j_schema=neo4j_schema, examples=examples) as rag:
            
            # Validate setup
            print("🔍 Validating system setup...")
            validation_result = rag.validate_setup()
            
            if not validation_result["text2cypher_rag"]:
                print("❌ System validation failed:")
                for error in validation_result["errors"]:
                    print(f"  - {error}")
                return
            
            print("✅ Text-to-Cypher RAG system ready!")
            print()
            
            # Display system information
            info = rag.get_info()
            print("📊 System Information:")
            print(f"  Type: {info['type']}")
            print(f"  Schema provided: {info['schema_provided']}")
            print(f"  Examples count: {info['examples_count']}")
            print(f"  Cypher LLM: {info['cypher_llm_info']['model_name']}")
            print(f"  Response LLM: {info['response_llm_info']['model_name']}")
            print()
            
            # Demonstrate schema extraction
            print("🔍 Extracting database schema...")
            try:
                extracted_schema = rag.get_schema_from_database()
                print("📋 Database Schema:")
                print(extracted_schema[:500] + "..." if len(extracted_schema) > 500 else extracted_schema)
                print()
            except Exception as e:
                print(f"⚠️  Schema extraction failed: {e}")
                print()
            
            # Example queries
            queries = [
                "Which movies did Hugo Weaving star in?",
                "What are some Action movies?",
                "Who directed the movie 'The Matrix'?",
                "What is the highest rating for the movie 'Goodfellas'?",
                "How many movies are in the database?",
                "What genres are available?"
            ]
            
            for i, query in enumerate(queries, 1):
                print(f"🔍 Query {i}: {query}")
                print("-" * 50)
                
                try:
                    # Generate and display Cypher query
                    print("🔧 Generating Cypher query...")
                    cypher_query = rag.generate_cypher(query)
                    print(f"📝 Generated Cypher: {cypher_query}")
                    print()
                    
                    # Perform full RAG search
                    print("🤖 Running RAG search...")
                    response = rag.search(
                        query_text=query,
                        return_context=True
                    )
                    
                    print("🤖 AI Response:")
                    print(response.answer)
                    print()
                    
                    if hasattr(response, 'retriever_result'):
                        print("📚 Retrieved Data:")
                        for j, item in enumerate(response.retriever_result.items[:3], 1):
                            print(f"  {j}. {item.content}")
                        print()
                    
                except Exception as e:
                    print(f"❌ Query failed: {e}")
                    print()
            
            # Demonstrate direct Cypher execution
            print("🔧 Testing direct Cypher execution...")
            try:
                direct_results = rag.execute_cypher("MATCH (m:Movie) RETURN m.title LIMIT 3")
                print("📊 Direct Cypher Results:")
                for result in direct_results:
                    print(f"  - {result}")
                print()
            except Exception as e:
                print(f"❌ Direct Cypher execution failed: {e}")
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
