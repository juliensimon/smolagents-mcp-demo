#!/usr/bin/env python3
"""
Unified Configuration Loader for MCP Demo

This module provides a centralized way to load and access configuration
for all components (clients, servers, tests) in the MCP demo project.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigLoader:
    """Centralized configuration loader for the MCP demo project."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.

        Args:
            config_path: Path to the configuration file. If None, uses default location.
        """
        if config_path is None:
            # Find the config file relative to this script
            script_dir = Path(__file__).parent
            config_path = str(script_dir / "config.json")

        self.config_path = Path(config_path)
        self._config: Optional[Dict[str, Any]] = None
        self._load_config()

    def _load_config(self):
        """Load the configuration from the JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        with open(self.config_path, "r") as f:
            self._config = json.load(f)

    def get_config(self) -> Dict[str, Any]:
        """Get the entire configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")
        return self._config

    def get_servers(self) -> Dict[str, Any]:
        """Get server configurations."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")
        return self._config.get("servers", {})

    def get_server_config(self, server_key: str) -> Dict[str, Any]:
        """Get configuration for a specific server."""
        servers = self.get_servers()
        if server_key not in servers:
            raise KeyError(f"Server '{server_key}' not found in configuration")
        return servers[server_key]

    def get_server_port(self, server_key: str) -> int:
        """Get the port number for a specific server."""
        server_config = self.get_server_config(server_key)
        port = server_config.get("port")
        if port is None:
            raise KeyError(f"Port not found for server '{server_key}'")
        return port

    def get_server_url(self, server_key: str) -> str:
        """Get the URL for a specific server."""
        server_config = self.get_server_config(server_key)
        url = server_config.get("url")
        if url is None:
            raise KeyError(f"URL not found for server '{server_key}'")
        return url

    def get_server_path(self, server_key: str) -> str:
        """Get the file path for a specific server."""
        server_config = self.get_server_config(server_key)
        path = server_config.get("path")
        if path is None:
            raise KeyError(f"Path not found for server '{server_key}'")
        return path

    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")
        return self._config.get("model", {})

    def get_model_default(self) -> str:
        """Get the default model name."""
        model_config = self.get_model_config()
        default = model_config.get("default")
        if default is None:
            raise KeyError("Default model not found in configuration")
        return default

    def get_model_api_base(self) -> str:
        """Get the model API base URL."""
        model_config = self.get_model_config()
        api_base = model_config.get("api_base")
        if api_base is None:
            raise KeyError("API base not found in configuration")
        return api_base

    def get_model_configs(self) -> Dict[str, Any]:
        """Get model-specific configurations."""
        model_config = self.get_model_config()
        return model_config.get("configs", {})

    def get_model_params(
        self, model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get parameters for a specific model."""
        if model_name is None:
            model_name = self.get_model_default()

        configs = self.get_model_configs()
        if model_name not in configs:
            raise KeyError(f"Model '{model_name}' not found in configuration")
        return configs[model_name]

    def get_client_config(self) -> Dict[str, Any]:
        """Get client configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")
        return self._config.get("client", {})

    def get_gradio_config(self) -> Dict[str, Any]:
        """Get Gradio-specific configuration."""
        client_config = self.get_client_config()
        return client_config.get("gradio", {})

    def get_testing_config(self) -> Dict[str, Any]:
        """Get testing configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")
        return self._config.get("testing", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")
        return self._config.get("logging", {})

    def get_all_server_ports(self) -> Dict[str, int]:
        """Get all server ports as a dictionary."""
        servers = self.get_servers()
        return {key: server.get("port") for key, server in servers.items()}

    def get_all_server_urls(self) -> Dict[str, str]:
        """Get all server URLs as a dictionary."""
        servers = self.get_servers()
        return {key: server.get("url") for key, server in servers.items()}

    def validate_config(self) -> bool:
        """Validate that the configuration is complete and correct."""
        try:
            if self._config is None:
                raise RuntimeError("Configuration not loaded")

            # Check required sections
            required_sections = [
                "servers",
                "model",
                "client",
                "testing",
                "logging",
            ]
            for section in required_sections:
                if section not in self._config:
                    raise ValueError(f"Missing required section: {section}")

            # Check servers
            servers = self.get_servers()
            if not servers:
                raise ValueError("No servers defined in configuration")

            for server_key, server_config in servers.items():
                required_server_fields = [
                    "name",
                    "port",
                    "url",
                    "description",
                    "path",
                ]
                for field in required_server_fields:
                    if field not in server_config:
                        raise ValueError(
                            f"Server '{server_key}' missing required field: {field}"
                        )

                # Validate port is a number
                if not isinstance(server_config["port"], int):
                    raise ValueError(
                        f"Server '{server_key}' port must be an integer"
                    )

                # Validate URL format
                url = server_config["url"]
                if (
                    not url.startswith("http://")
                    or "gradio_api/mcp/sse" not in url
                ):
                    raise ValueError(
                        f"Server '{server_key}' URL format is invalid"
                    )

            # Check model configuration
            model_config = self.get_model_config()
            if "default" not in model_config:
                raise ValueError("Model configuration missing 'default' field")

            default_model = model_config["default"]
            configs = self.get_model_configs()
            if default_model not in configs:
                raise ValueError(
                    f"Default model '{default_model}' not found in model configs"
                )

            return True

        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global configuration loader instance
_config_loader = None


def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


# Convenience functions for common configuration access
def get_server_port(server_key: str) -> int:
    """Get the port number for a specific server."""
    return get_config_loader().get_server_port(server_key)


def get_server_url(server_key: str) -> str:
    """Get the URL for a specific server."""
    return get_config_loader().get_server_url(server_key)


def get_model_params(model_name: Optional[str] = None) -> Dict[str, Any]:
    """Get parameters for a specific model."""
    return get_config_loader().get_model_params(model_name)


def get_gradio_config() -> Dict[str, Any]:
    """Get Gradio configuration."""
    return get_config_loader().get_gradio_config()


def get_testing_config() -> Dict[str, Any]:
    """Get testing configuration."""
    return get_config_loader().get_testing_config()


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return get_config_loader().get_logging_config()


if __name__ == "__main__":
    # Test the configuration loader
    try:
        config_loader = ConfigLoader()
        if config_loader.validate_config():
            print("✅ Configuration is valid")
            print(
                f"Available servers: {list(config_loader.get_servers().keys())}"
            )
            print(f"Default model: {config_loader.get_model_default()}")
        else:
            print("❌ Configuration validation failed")
            exit(1)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        exit(1)
