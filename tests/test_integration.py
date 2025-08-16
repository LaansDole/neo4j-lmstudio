#!/usr/bin/env python3
"""
Test suite for Neo4j LMStudio Integration

This module provides comprehensive tests for all components
of the Neo4j LMStudio integration package.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from neo4j_lmstudio.config.settings import Settings, get_settings
from neo4j_lmstudio.core.client import LMStudioClient
from neo4j_lmstudio.utils.helpers import HealthChecker, ConnectionManager


class TestSettings(unittest.TestCase):
    """Test configuration management."""
    
    def test_settings_initialization(self):
        """Test settings can be initialized."""
        settings = Settings()
        self.assertIsNotNone(settings)
        self.assertIsNotNone(settings.lmstudio)
        self.assertIsNotNone(settings.neo4j)
        self.assertIsNotNone(settings.rag)
    
    def test_settings_validation(self):
        """Test settings validation."""
        settings = Settings()
        validation = settings.validate()
        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
        self.assertIn("errors", validation)
        self.assertIn("warnings", validation)
    
    def test_settings_to_dict(self):
        """Test settings conversion to dictionary."""
        settings = Settings()
        settings_dict = settings.to_dict()
        self.assertIsInstance(settings_dict, dict)
        self.assertIn("lmstudio", settings_dict)
        self.assertIn("neo4j", settings_dict)
        self.assertIn("rag", settings_dict)


class TestLMStudioClient(unittest.TestCase):
    """Test LMStudio client functionality."""
    
    @patch('neo4j_lmstudio.core.client.OpenAI')
    def test_client_initialization(self, mock_openai):
        """Test client initialization."""
        mock_openai.return_value = Mock()
        client = LMStudioClient()
        self.assertIsNotNone(client)
        self.assertIsNotNone(client.client)
    
    @patch('neo4j_lmstudio.core.client.OpenAI')
    def test_health_check(self, mock_openai):
        """Test health check functionality."""
        mock_client = Mock()
        mock_models = Mock()
        mock_models.data = [Mock()]
        mock_client.models.list.return_value = mock_models
        mock_openai.return_value = mock_client
        
        client = LMStudioClient()
        result = client.health_check()
        self.assertTrue(result)
    
    @patch('neo4j_lmstudio.core.client.OpenAI')
    def test_list_models(self, mock_openai):
        """Test model listing."""
        mock_client = Mock()
        mock_models = Mock()
        mock_model = Mock()
        mock_model.id = "test-model"
        mock_models.data = [mock_model]
        mock_client.models.list.return_value = mock_models
        mock_openai.return_value = mock_client
        
        client = LMStudioClient()
        result = client.list_models()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["count"], 1)
        self.assertIn("test-model", result["models"])


class TestConnectionManager(unittest.TestCase):
    """Test connection management."""
    
    def test_connection_manager_initialization(self):
        """Test connection manager initialization."""
        manager = ConnectionManager()
        self.assertIsNotNone(manager)
    
    @patch('neo4j_lmstudio.utils.helpers.GraphDatabase')
    def test_neo4j_driver_creation(self, mock_graph_db):
        """Test Neo4j driver creation."""
        mock_driver = Mock()
        mock_graph_db.driver.return_value = mock_driver
        
        manager = ConnectionManager()
        driver = manager.get_neo4j_driver()
        self.assertIsNotNone(driver)
    
    def test_lmstudio_client_creation(self):
        """Test LMStudio client creation."""
        manager = ConnectionManager()
        client = manager.get_lmstudio_client()
        self.assertIsNotNone(client)


class TestHealthChecker(unittest.TestCase):
    """Test health checking functionality."""
    
    def test_health_checker_initialization(self):
        """Test health checker initialization."""
        checker = HealthChecker()
        self.assertIsNotNone(checker)
    
    @patch('neo4j_lmstudio.utils.helpers.ConnectionManager')
    def test_check_all_health_structure(self, mock_connection_manager):
        """Test that check_all_health returns proper structure."""
        mock_manager = Mock()
        mock_connection_manager.return_value = mock_manager
        
        checker = HealthChecker(mock_manager)
        
        # Mock the individual health check methods to avoid actual connections
        checker.check_neo4j_health = Mock(return_value={
            "service": "neo4j", "healthy": True, "response_time_ms": 100
        })
        checker.check_lmstudio_health = Mock(return_value={
            "service": "lmstudio", "healthy": True, "response_time_ms": 200
        })
        checker.check_embedder_health = Mock(return_value={
            "service": "embedder", "healthy": True, "response_time_ms": 300
        })
        checker.check_llm_health = Mock(return_value={
            "service": "llm", "healthy": True, "response_time_ms": 400
        })
        
        result = checker.check_all_health()
        
        self.assertIsInstance(result, dict)
        self.assertIn("overall_healthy", result)
        self.assertIn("timestamp", result)
        self.assertIn("components", result)
        self.assertEqual(len(result["components"]), 4)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def test_package_imports(self):
        """Test that all main components can be imported."""
        try:
            from neo4j_lmstudio import VectorRAG, VectorCypherRAG, Text2CypherRAG
            from neo4j_lmstudio import LMStudioClient, LMStudioEmbedder, LMStudioLLM
            from neo4j_lmstudio import Settings
            self.assertTrue(True)  # If we get here, imports worked
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_settings_global_access(self):
        """Test global settings access."""
        settings = get_settings()
        self.assertIsNotNone(settings)
        self.assertIsInstance(settings, Settings)


def run_tests():
    """Run all tests."""
    print("🧪 Running Neo4j LMStudio Integration Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSettings,
        TestLMStudioClient,
        TestConnectionManager,
        TestHealthChecker,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("\nErrors:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"\nOverall: {status}")
    
    return success


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
