# Neo4j LMStudio Integration

A production-ready Python package for integrating Neo4j graph databases with LMStudio local language models, providing powerful RAG (Retrieval-Augmented Generation) capabilities for knowledge graphs.

## 🌟 Features

- **Local AI Integration**: Use LMStudio's local language models without external API dependencies
- **Multiple RAG Patterns**: Vector-based, Vector-Cypher, and Text-to-Cypher retrieval strategies
- **Production Ready**: Comprehensive error handling, configuration management, and health monitoring
- **Easy to Use**: Simple APIs with sensible defaults and extensive documentation
- **Privacy First**: All data processing happens locally with no external API calls

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd neo4j-localai

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Prerequisites

1. **LMStudio**: Download and install [LMStudio](https://lmstudio.ai)
   - Download models (e.g., `meta-llama-3.1-8b-instruct`, `nomic-ai/nomic-embed-text-v1.5`)
   - Start the local server

2. **Neo4j Database**: Set up a Neo4j instance with your data
   - Neo4j Desktop, AuraDB, or self-hosted
   - Create vector indices for embeddings

### Configuration

Create a `.env` file in the project root:

```env
# LMStudio Configuration
LMSTUDIO_CHAT_MODEL="meta-llama-3.1-8b-instruct"
LMSTUDIO_EMBEDDING_MODEL="nomic-ai/nomic-embed-text-v1.5"
LMSTUDIO_API_HOST="http://127.0.0.1:1234/v1"

# Neo4j Database Configuration
NEO4J_URI="neo4j://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-password"

# RAG Configuration
RAG_VECTOR_INDEX_NAME="moviePlots"
RAG_TOP_K=5
```

### Basic Usage

#### Vector RAG

```python
from neo4j_lmstudio import VectorRAG

# Initialize and use Vector RAG
with VectorRAG() as rag:
    response = rag.search(
        query_text="Find movies about space exploration",
        top_k=5,
        return_context=True
    )
    print(response.answer)
```

#### Text-to-Cypher RAG

```python
from neo4j_lmstudio import Text2CypherRAG

# Initialize Text-to-Cypher RAG
with Text2CypherRAG() as rag:
    response = rag.search(
        query_text="Which actors starred in The Matrix?",
        return_context=True
    )
    print(response.answer)
    print(f"Generated Cypher: {response.retriever_result.metadata['cypher']}")
```

#### Health Checking

```python
from neo4j_lmstudio.utils.helpers import HealthChecker

# Check system health
checker = HealthChecker()
health_result = checker.check_all_health()

if health_result["overall_healthy"]:
    print("✅ All systems operational")
else:
    print("❌ System issues detected")
    for component, status in health_result["components"].items():
        if not status["healthy"]:
            print(f"  {component}: {status['error']}")
```

## 📚 Architecture

### Package Structure

```
src/neo4j_lmstudio/
├── __init__.py              # Main package exports
├── core/                    # Core functionality
│   ├── client.py           # LMStudio client management
│   ├── embeddings.py       # Embedding implementations
│   └── llm.py              # LLM implementations
├── rag/                     # RAG implementations
│   ├── vector_rag.py       # Vector-based RAG
│   ├── vector_cypher_rag.py # Vector + Cypher RAG
│   └── text2cypher_rag.py  # Text-to-Cypher RAG
├── config/                  # Configuration management
│   └── settings.py         # Settings and validation
└── utils/                   # Utility functions
    └── helpers.py          # Health checks, connections
```

### RAG Strategies

1. **Vector RAG**: Uses vector similarity search on Neo4j vector indices
2. **Vector-Cypher RAG**: Combines vector search with custom Cypher queries
3. **Text-to-Cypher RAG**: Converts natural language to Cypher queries

## 🔧 Configuration

The package uses a hierarchical configuration system:

1. **Default values** in code
2. **Environment variables** (`.env` file)
3. **Runtime configuration** via Settings class

### Configuration Options

#### LMStudio Settings
- `LMSTUDIO_API_HOST`: LMStudio server URL
- `LMSTUDIO_CHAT_MODEL`: Chat completion model
- `LMSTUDIO_EMBEDDING_MODEL`: Text embedding model
- `LMSTUDIO_TEMPERATURE`: Generation temperature
- `LMSTUDIO_MAX_TOKENS`: Maximum tokens to generate

#### Neo4j Settings
- `NEO4J_URI`: Database connection URI
- `NEO4J_USERNAME`: Database username
- `NEO4J_PASSWORD`: Database password
- `NEO4J_DATABASE`: Database name

#### RAG Settings
- `RAG_VECTOR_INDEX_NAME`: Vector index name
- `RAG_TOP_K`: Number of results to retrieve
- `RAG_SIMILARITY_THRESHOLD`: Minimum similarity score
- `RAG_BATCH_SIZE`: Embedding batch size

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python tests/test_integration.py

# Run examples
python examples/vector_rag_example.py
python examples/text2cypher_rag_example.py
python examples/health_check_example.py
```

## 📖 Examples

See the `examples/` directory for comprehensive usage examples:

- `vector_rag_example.py`: Vector-based movie recommendations
- `text2cypher_rag_example.py`: Natural language to Cypher queries
- `health_check_example.py`: System health monitoring

## 🔍 Monitoring & Health Checks

The package includes comprehensive health monitoring:

```python
from neo4j_lmstudio.utils.helpers import HealthChecker

checker = HealthChecker()

# Check individual components
neo4j_health = checker.check_neo4j_health()
lmstudio_health = checker.check_lmstudio_health()

# Comprehensive health check
overall_health = checker.check_all_health()
```

## 🛠️ Development

### Project Commands

```bash
# Format code
make format

# Run linting
make lint

# Run tests
make test

# Check LMStudio status
make lmstudio-status

# Run examples
make run-examples
```

### Adding New RAG Strategies

1. Create a new class in `src/neo4j_lmstudio/rag/`
2. Implement the required interface methods
3. Add to `__init__.py` exports
4. Create examples and tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Support

- Check the health monitoring tools for diagnostic information
- Review the examples for usage patterns
- Ensure LMStudio and Neo4j are properly configured

## 🔄 Migration from Learning Structure

This project has been transformed from a learning-oriented course structure to a production-ready package. The old `genai-fundamentals/` directory structure has been replaced with a proper Python package in `src/neo4j_lmstudio/`.

### Key Changes:
- Consolidated duplicate implementations
- Added proper configuration management
- Implemented comprehensive error handling
- Added health monitoring and validation
- Created production-ready APIs
- Improved documentation and examples
