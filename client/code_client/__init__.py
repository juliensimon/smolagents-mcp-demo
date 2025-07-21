"""
Multi-Server MCP Client Package

A unified client that connects to multiple MCP servers for code analysis,
security scanning, git operations, and file retrieval.
"""

# Import the wrapper functions from client.py
from .client import (
    MultiServerMCPClient,
    load_api_base,
    load_config,
    load_servers,
)

__version__ = "1.0.0"
__author__ = "MCP Demo Team"

__all__ = [
    "MultiServerMCPClient",
    "load_config",
    "load_servers",
    "load_api_base",
]
