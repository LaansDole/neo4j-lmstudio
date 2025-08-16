"""
Setup script for Neo4j LMStudio Integration package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'docs', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Neo4j LMStudio Integration Package"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove comments and version constraints for development dependencies
                    if 'pytest' in line or 'flake8' in line or 'black' in line or 'isort' in line or 'mypy' in line:
                        continue
                    requirements.append(line)
    return requirements

setup(
    name="neo4j-lmstudio",
    version="1.0.0",
    description="Production-ready Neo4j and LMStudio integration for RAG applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Neo4j LMStudio Team",
    author_email="contact@example.com",
    url="https://github.com/your-org/neo4j-localai",
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=8.3.4",
            "flake8>=7.2.0",
            "black>=24.8.0",
            "isort>=5.13.2",
            "mypy>=1.11.2",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "neo4j-lmstudio-health=neo4j_lmstudio.utils.helpers:main",
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    keywords="neo4j lmstudio rag ai llm embedding graph database knowledge graph",
    
    # Include additional files
    include_package_data=True,
    package_data={
        "neo4j_lmstudio": ["*.md", "*.txt"],
    },
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/your-org/neo4j-localai/issues",
        "Source": "https://github.com/your-org/neo4j-localai",
        "Documentation": "https://github.com/your-org/neo4j-localai/blob/main/docs/README.md",
    },
)
