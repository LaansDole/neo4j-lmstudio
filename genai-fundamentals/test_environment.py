# This will test the environment to ensure that the .env file is set up
# correctly and that the LM Studio and Neo4j connections are working.
import os
import unittest

from dotenv import find_dotenv, load_dotenv
from lmstudio_client import get_lmstudio_llm

load_dotenv()


class TestEnvironment(unittest.TestCase):

    skip_env_variable_tests = True
    skip_lmstudio_test = True
    skip_neo4j_test = True

    def test_env_file_exists(self):
        env_file_exists = True if find_dotenv() > "" else False
        if env_file_exists:
            TestEnvironment.skip_env_variable_tests = False
        self.assertTrue(env_file_exists, ".env file not found.")

    def env_variable_exists(self, variable_name):
        self.assertIsNotNone(os.getenv(variable_name), f"{variable_name} not found in .env file")

    def test_lmstudio_variables(self):
        if TestEnvironment.skip_env_variable_tests:
            self.skipTest("Skipping LM Studio env variable test")

        self.env_variable_exists("LMSTUDIO_CHAT_MODEL")
        self.env_variable_exists("LMSTUDIO_EMBEDDING_MODEL")
        TestEnvironment.skip_lmstudio_test = False

    def test_neo4j_variables(self):
        if TestEnvironment.skip_env_variable_tests:
            self.skipTest("Skipping Neo4j env variables test")

        self.env_variable_exists("NEO4J_URI")
        self.env_variable_exists("NEO4J_USERNAME")
        self.env_variable_exists("NEO4J_PASSWORD")
        TestEnvironment.skip_neo4j_test = False

    def test_lmstudio_connection(self):
        if TestEnvironment.skip_lmstudio_test:
            self.skipTest("Skipping LM Studio test")

        try:
            get_lmstudio_llm()
            # Try to get model info to verify connection
            connection_successful = True
        except Exception:
            connection_successful = False

        self.assertTrue(
            connection_successful,
            "LM Studio connection failed. Check that LM Studio desktop app is running and models are loaded.",
        )

    def test_neo4j_connection(self):
        if TestEnvironment.skip_neo4j_test:
            self.skipTest("Skipping Neo4j connection test")

        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))
        try:
            driver.verify_connectivity()
            connected = True
        except Exception:
            connected = False

        driver.close()

        self.assertTrue(
            connected, "Neo4j connection failed. Check the NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD values in .env file."
        )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestEnvironment("test_env_file_exists"))
    suite.addTest(TestEnvironment("test_lmstudio_variables"))
    suite.addTest(TestEnvironment("test_neo4j_variables"))
    suite.addTest(TestEnvironment("test_lmstudio_connection"))
    suite.addTest(TestEnvironment("test_neo4j_connection"))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
