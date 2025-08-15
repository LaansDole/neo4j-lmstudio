# Neo4j LocalAI Project Makefile
# 
# This Makefile provides common development tasks for testing, linting,
# and running the Neo4j + LM Studio integration project.

.PHONY: help ngrok install test test-env test-solutions lint format check-style clean setup dev-setup run-examples lmstudio-status all

# Default target
help: ## Show this help message
	@echo "Neo4j LocalAI Project - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Python virtual environment activated"
	@echo "  - LM Studio desktop app installed and running"
	@echo "  - Neo4j database running (for full tests)"

# Variables
PYTHON := python3
PIP := pip
VENV_DIR := venv
SRC_DIR := genai-fundamentals
TEST_OPTIONS := -v

# === Environment Setup ===

ngrok:
	ngrok http --url=sset-localai.ngrok.io 1234 --pooling-enabled=true

install: ## Install project dependencies
	$(PIP) install -r requirements.txt

dev-install: ## Install development dependencies including linting tools
	$(PIP) install -r requirements.txt
	$(PIP) install pytest flake8 black isort mypy

setup: ## Set up the development environment
	@echo "Setting up development environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi
	@echo "Virtual environment ready. Activate with: source $(VENV_DIR)/bin/activate"
	@echo "Then run: make dev-install"

# === Testing ===

chat: ## Run chat tests
	$(PYTHON) tool-use-example.py

test: ## Run all tests
	$(PYTHON) -m pytest $(TEST_OPTIONS)

test-env: ## Run environment tests only (basic setup validation)
	$(PYTHON) -m pytest $(SRC_DIR)/test_environment.py $(TEST_OPTIONS)

test-solutions: ## Run solution tests (requires LM Studio running)
	$(PYTHON) -m pytest $(SRC_DIR)/solutions/test_solutions.py $(TEST_OPTIONS)

test-quick: ## Run tests without LM Studio dependency
	$(PYTHON) -m pytest $(SRC_DIR)/test_environment.py::TestEnvironment::test_env_file_exists $(TEST_OPTIONS)
	$(PYTHON) -m pytest $(SRC_DIR)/test_environment.py::TestEnvironment::test_lmstudio_variables $(TEST_OPTIONS)
	$(PYTHON) -m pytest $(SRC_DIR)/test_environment.py::TestEnvironment::test_neo4j_variables $(TEST_OPTIONS)

# === Code Quality ===

lint: ## Run linting checks
	@echo "Running flake8 linting..."
	$(PYTHON) -m flake8 $(SRC_DIR)/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "Running full flake8 with style checks..."
	$(PYTHON) -m flake8 $(SRC_DIR)/ --count --max-complexity=10 --max-line-length=127 --statistics || true

format: ## Format code with black and isort
	@echo "Formatting code with black..."
	$(PYTHON) -m black $(SRC_DIR)/ --line-length=127
	@echo "Organizing imports with isort..."
	$(PYTHON) -m isort $(SRC_DIR)/ --profile black --line-length 127

check-style: ## Check code style without making changes
	@echo "Checking code style..."
	$(PYTHON) -m black $(SRC_DIR)/ --line-length=127 --check --diff
	$(PYTHON) -m isort $(SRC_DIR)/ --profile black --line-length 127 --check-only --diff

mypy: ## Run type checking (optional)
	@echo "Running mypy type checking..."
	$(PYTHON) -m mypy $(SRC_DIR)/ --ignore-missing-imports || true

# === Running Examples ===

run-examples: ## Run all example scripts (requires LM Studio and Neo4j running)
	@echo "Running example scripts..."
	@echo "Note: LM Studio and Neo4j must be running"
	@echo ""
	@echo "1. Running Vector Retriever example..."
	$(PYTHON) $(SRC_DIR)/vector_retriever.py || true
	@echo ""
	@echo "2. Running Vector RAG example..."
	$(PYTHON) $(SRC_DIR)/vector_rag.py || true
	@echo ""
	@echo "3. Running Vector Cypher RAG example..."
	$(PYTHON) $(SRC_DIR)/vector_cypher_rag.py || true
	@echo ""
	@echo "4. Running Text2Cypher RAG example..."
	$(PYTHON) $(SRC_DIR)/text2cypher_rag.py || true

run-solutions: ## Run solution examples (requires LM Studio and Neo4j running)
	@echo "Running solution examples..."
	@echo "Note: LM Studio and Neo4j must be running"
	@echo ""
	@echo "1. Running Text2Cypher RAG with examples..."
	$(PYTHON) $(SRC_DIR)/solutions/text2cypher_rag_examples.py || true
	@echo ""
	@echo "2. Running Text2Cypher RAG with schema..."
	$(PYTHON) $(SRC_DIR)/solutions/text2cypher_rag_schema.py || true

# === LM Studio Management ===

lmstudio-status: ## Check LM Studio server status
	@echo "Checking LM Studio server status..."
	@curl -s http://localhost:1234/v1/models > /dev/null 2>&1 && \
		echo "✅ LM Studio server is running" || \
		echo "❌ LM Studio server is not reachable at localhost:1234"

lmstudio-models: ## List available LM Studio models
	@echo "Available LM Studio models:"
	@curl -s http://localhost:1234/v1/models 2>/dev/null | $(PYTHON) -m json.tool || \
		echo "❌ Cannot connect to LM Studio server"

# === Development Workflow ===

dev-check: ## Run comprehensive development checks
	@echo "Running comprehensive development checks..."
	make format
	make lint
	make test-quick

ci-check: ## Run CI-style checks (for automated testing)
	@echo "Running CI checks..."
	make check-style
	$(PYTHON) -m flake8 $(SRC_DIR)/ --count --max-complexity=10 --max-line-length=127 --exit-zero
	make test-env

all: ## Run all checks and tests
	@echo "Running complete test suite..."
	make format
	make lint
	make test

# === Utility ===

clean: ## Clean up generated files
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

env-info: ## Show environment information
	@echo "Environment Information:"
	@echo "========================"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Virtual environment: $${VIRTUAL_ENV:-Not activated}"
	@echo "Current directory: $$(pwd)"
	@echo "LM Studio status: $$(curl -s http://localhost:1234/v1/models > /dev/null 2>&1 && echo 'Running' || echo 'Not running')"

# === Server Commands ===

server-env: ## Run environment test server
	@echo "Running environment validation..."
	$(PYTHON) $(SRC_DIR)/test_environment.py

# Note: This project doesn't have a traditional web server, but rather
# consists of example scripts that demonstrate Neo4j + LM Studio integration.
# The "server" in this context refers to running the example applications.

# === Quick Commands ===

quick: dev-check ## Quick development check (format + lint + basic tests)

full: all ## Full test suite with all checks
