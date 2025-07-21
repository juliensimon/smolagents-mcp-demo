"""
Multi-Server MCP Client Package

A unified client that connects to multiple MCP servers for code analysis,
security scanning, git operations, and file retrieval.
"""

# Import the wrapper functions from client.py
from .client import (
    MultiServerMCPClient,
    get_status,
    initialize_client,
    load_api_base,
    load_config,
    load_servers,
    process_message,
)

__version__ = "1.0.0"
__author__ = "MCP Demo Team"

__all__ = [
    "MultiServerMCPClient",
    "initialize_client",
    "process_message",
    "get_status",
    "load_config",
    "load_servers",
    "load_api_base",
]
