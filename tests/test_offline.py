#!/usr/bin/env python3
"""
Offline Tests - Tests that can run without live MCP servers or endpoints

These tests are safe to run in CI environments where servers are not available.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import from tests
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config_loader import get_config_loader


class TestConfigurationOffline(unittest.TestCase):
    """Test configuration structure and validation without requiring servers."""

    def setUp(self):
        """Set up test environment."""
        self.config_loader = get_config_loader()
        # Get the project root directory
        self.project_root = Path(__file__).parent.parent

    def test_config_structure(self):
        """Test that configuration has the expected structure."""
        config = self.config_loader.get_config()

        # Check required top-level keys
        required_keys = ["servers", "model", "client", "testing", "logging"]
        for key in required_keys:
            self.assertIn(key, config, f"Missing required config key: {key}")

        # Check servers configuration
        servers = config["servers"]
        self.assertIsInstance(servers, dict, "Servers should be a dictionary")

        # Check each server has required fields
        for server_key, server_config in servers.items():
            required_server_keys = ["name", "url", "port"]
            for key in required_server_keys:
                self.assertIn(
                    key, server_config, f"Server {server_key} missing {key}"
                )

        # Check model configuration
        model_config = config["model"]
        self.assertIn(
            "default", model_config, "Model config missing default model"
        )
        self.assertIn(
            "api_base", model_config, "Model config missing api_base"
        )
        self.assertIn("configs", model_config, "Model config missing configs")

    def test_server_urls_valid(self):
        """Test that server URLs have valid format."""
        servers = self.config_loader.get_servers()

        for server_key, server_config in servers.items():
            url = server_config["url"]
            self.assertTrue(
                url.startswith(("http://", "https://")),
                f"Invalid URL format for {server_key}: {url}",
            )

    def test_server_ports_unique(self):
        """Test that server ports are unique."""
        servers = self.config_loader.get_servers()
        ports = []

        for server_key, server_config in servers.items():
            port = server_config["port"]
            self.assertNotIn(
                port, ports, f"Duplicate port {port} for server {server_key}"
            )
            ports.append(port)

    def test_model_configuration(self):
        """Test model configuration structure."""
        model_config = self.config_loader.get_model_config()

        # Check required fields
        self.assertIn("default", model_config, "Missing default model")
        self.assertIn("api_base", model_config, "Missing API base URL")
        self.assertIn("configs", model_config, "Missing model configs")

        # Check that default model is a string
        self.assertIsInstance(
            model_config["default"], str, "Default model should be string"
        )

        # Check that API base is a valid URL
        api_base = model_config["api_base"]
        self.assertTrue(
            api_base.startswith(("http://", "https://")),
            f"Invalid API base URL: {api_base}",
        )

    def test_configuration_validation(self):
        """Test configuration validation methods."""
        # Test that we can get server configs
        servers = self.config_loader.get_servers()
        self.assertIsInstance(servers, dict)
        self.assertGreater(len(servers), 0)

        # Test that we can get model config
        model_config = self.config_loader.get_model_config()
        self.assertIsInstance(model_config, dict)
        self.assertIn("default", model_config)

        # Test that we can get model params
        model_params = self.config_loader.get_model_params()
        self.assertIsInstance(model_params, dict)

    def test_server_paths_exist(self):
        """Test that server paths exist in the filesystem."""
        servers = self.config_loader.get_servers()

        for server_key, server_config in servers.items():
            if "path" in server_config:
                server_path = self.project_root / server_config["path"]
                self.assertTrue(
                    server_path.exists(),
                    f"Server path does not exist: {server_path}",
                )


class TestEnvironmentOffline(unittest.TestCase):
    """Test environment setup without requiring servers."""

    def test_environment_variables(self):
        """Test that required environment variables are documented."""
        # This test checks that we can access environment variables
        # It doesn't require them to be set, just that the code can handle them
        api_key = os.getenv("TOGETHER_API_KEY")
        # Should not raise an exception whether the key exists or not
        self.assertIsInstance(api_key, (str, type(None)))

    def test_dependencies_available(self):
        """Test that required Python packages can be imported."""
        try:
            import json
            import pathlib
            import tempfile
            import time
            import unittest

            import requests

            # These are core dependencies that should be available
            self.assertTrue(True, "Core dependencies are available")
        except ImportError as e:
            self.fail(f"Missing required dependency: {e}")

    def test_configuration_validation(self):
        """Test that configuration validation works."""
        try:
            config_loader = get_config_loader()
            config = config_loader.get_config()
            self.assertIsInstance(config, dict)
            self.assertIn("servers", config)
        except Exception as e:
            self.fail(f"Configuration validation failed: {e}")

    def test_python_version(self):
        """Test that Python version is compatible."""
        import sys

        version = sys.version_info

        # Check minimum Python version (3.8+)
        self.assertGreaterEqual(version.major, 3, "Python 3.x required")
        if version.major == 3:
            self.assertGreaterEqual(version.minor, 8, "Python 3.8+ required")


class TestConfigValidationOffline(unittest.TestCase):
    """Test configuration validation without requiring servers."""

    def setUp(self):
        """Set up test environment."""
        self.config_loader = get_config_loader()
        self.project_root = Path(__file__).parent.parent

    def test_config_file_exists(self):
        """Test that config.json file exists."""
        config_path = self.project_root / "config.json"
        self.assertTrue(config_path.exists(), "config.json file should exist")

    def test_config_file_valid_json(self):
        """Test that config.json is valid JSON."""
        try:
            config = self.config_loader.get_config()
            self.assertIsInstance(config, dict)
        except Exception as e:
            self.fail(f"config.json is not valid JSON: {e}")

    def test_server_configs_complete(self):
        """Test that all server configurations are complete."""
        servers = self.config_loader.get_servers()

        for server_key, server_config in servers.items():
            # Check required fields
            required_fields = ["name", "url", "port"]
            for field in required_fields:
                self.assertIn(
                    field,
                    server_config,
                    f"Server {server_key} missing {field}",
                )
                self.assertIsNotNone(
                    server_config[field],
                    f"Server {server_key} {field} is None",
                )

    def test_model_params_structure(self):
        """Test that model parameters have correct structure."""
        model_params = self.config_loader.get_model_params()
        self.assertIsInstance(model_params, dict)

        # Check for common model parameters
        if model_params:
            # If there are parameters, they should be valid
            for key, value in model_params.items():
                self.assertIsInstance(
                    key, str, f"Model parameter key should be string: {key}"
                )
                # Value can be any type, just check it's not None if it's a required field
                if key in ["temperature", "max_tokens"]:
                    self.assertIsNotNone(
                        value, f"Model parameter {key} should not be None"
                    )


class TestFileStructureOffline(unittest.TestCase):
    """Test file structure and imports without requiring servers."""

    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent

    def test_server_modules_importable(self):
        """Test that server modules can be imported."""
        try:
            # Test that we can import the modules (they don't export classes)
            import server.basic_server.basic_server
            import server.code_metrics_server.code_metrics_server
            import server.code_retriever_server.code_retriever_server
            import server.code_security_server.code_security_server
            import server.git_server.git_server

            self.assertTrue(True, "All server modules can be imported")
        except ImportError as e:
            self.fail(f"Failed to import server module: {e}")

    def test_client_modules_importable(self):
        """Test that client modules can be imported."""
        try:
            # Test that we can import the modules (they don't export classes)
            import client.basic_client.client
            import client.code_client.client
            import client.multi_agent_client.client

            self.assertTrue(True, "All client modules can be imported")
        except ImportError as e:
            self.fail(f"Failed to import client module: {e}")

    def test_required_files_exist(self):
        """Test that required files exist."""
        required_files = [
            "config.json",
            "requirements.txt",
            "README.md",
            "config_loader.py",
            "start_all_servers.py",
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            self.assertTrue(
                full_path.exists(),
                f"Required file does not exist: {file_path}",
            )

    def test_directory_structure(self):
        """Test that directory structure is correct."""
        required_dirs = ["server", "client", "tests"]

        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            self.assertTrue(
                full_path.is_dir(),
                f"Required directory does not exist: {dir_path}",
            )


if __name__ == "__main__":
    unittest.main()
