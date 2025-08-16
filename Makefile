# Neo4j LMStudio Integration Makefile
# 
# This Makefile provides common development tasks for the production-ready
# Neo4j + LMStudio integration package.

.PHONY: help install lint format check-style clean setup dev-install run-examples health-check all

# Default target
help: ## Show this help message
	@echo "Neo4j LMStudio Integration - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Python virtual environment activated"
	@echo "  - LMStudio desktop app installed and running"
	@echo "  - Neo4j database running (for full functionality)"

# Variables
PYTHON := python3
PIP := pip
VENV_DIR := venv
SRC_DIR := src

# === Environment Setup ===

install: ## Install package and dependencies
	$(PIP) install -e .

dev-install: ## Install package in development mode with dev dependencies
	$(PIP) install -e ".[dev]"

setup: ## Set up the development environment
	@echo "Setting up development environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi
	@echo "Virtual environment ready. Activate with: source $(VENV_DIR)/bin/activate"
	@echo "Then run: make dev-install"

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

mypy: ## Run type checking
	@echo "Running mypy type checking..."
	$(PYTHON) -m mypy $(SRC_DIR)/ --ignore-missing-imports || true

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

ci-check: ## Run CI-style checks (for automated testing)
	@echo "Running CI checks..."
	make check-style
	$(PYTHON) -m flake8 $(SRC_DIR)/ --count --max-complexity=10 --max-line-length=127 --exit-zero

all: ## Run all checks and tests
	@echo "Running complete development workflow..."
	make format
	make lint

# === Package Management ===

build: ## Build the package
	$(PYTHON) setup.py sdist bdist_wheel

install-package: ## Install the package locally
	$(PIP) install -e .

uninstall-package: ## Uninstall the package
	$(PIP) uninstall neo4j-lmstudio -y

# === Utility ===

clean: ## Clean up generated files
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true

env-info: ## Show environment information
	@echo "Environment Information:"
	@echo "========================"
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Virtual environment: $${VIRTUAL_ENV:-Not activated}"
	@echo "Current directory: $$(pwd)"
	@echo "Package installed: $$($(PIP) show neo4j-lmstudio >/dev/null 2>&1 && echo 'Yes' || echo 'No')"
	@echo "LM Studio status: $$(curl -s http://localhost:1234/v1/models > /dev/null 2>&1 && echo 'Running' || echo 'Not running')"

# === Utility Commands ===

chat:
	$(PYTHON) tool-use-example.py

# === Quick Commands ===

quick: dev-check ## Quick development check (format + lint + basic tests)

full: all ## Full development workflow
