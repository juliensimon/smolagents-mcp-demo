#!/usr/bin/env python3
"""
Logging utilities for MCP servers
"""

import logging
import re
from typing import Any, Dict


class ToolCallFilter(logging.Filter):
    """Filter to exclude ListToolsRequest and ensure tool calls are visible."""

    def __init__(self, name: str = ""):
        super().__init__(name)
        self.exclude_patterns = [
            r"ListToolsRequest",
            r"Processing request of type ListToolsRequest",
            r"mcp\.server\.lowlevel\.server.*ListToolsRequest",
            r"mcp\.server\.lowlevel\.server.*Processing request of type",
        ]
        self.include_patterns = [
            r"🔧 TOOL CALL:",
            r"✅ TOOL RESULT:",
            r"tool",
            r"Tool",
            r"CallTool",
            r"call_tool",
            r"tool_call",
            r"ToolCall",
        ]

    def filter(self, record):
        message = record.getMessage()

        # Exclude ListToolsRequest messages
        for pattern in self.exclude_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False

        # Include tool-related messages
        for pattern in self.include_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True

        # For other messages, use default behavior
        return True


def setup_logging(logging_config: Dict[str, Any]) -> logging.Logger:
    """Setup logging with custom filters."""

    log_file = logging_config.get("file", "mcp_servers.log")
    log_level = getattr(logging, logging_config.get("level", "INFO"))
    log_format = logging_config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # Only errors to console

    # Add custom filter to file handler
    file_handler.addFilter(ToolCallFilter())

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[file_handler, console_handler],
    )

    # Set MCP server framework logging level from config
    mcp_log_level = logging_config.get("mcp_logging_level", "ERROR")
    mcp_log_level = getattr(logging, mcp_log_level)
    logging.getLogger("mcp.server.lowlevel.server").setLevel(mcp_log_level)
    logging.getLogger("mcp.server").setLevel(mcp_log_level)
    logging.getLogger("mcp").setLevel(mcp_log_level)

    return logging.getLogger(__name__)


def log_tool_call(
    logger: logging.Logger, tool_name: str, args: Dict[str, Any] = None
):
    """Log a tool call with standardized format."""
    args_str = f" with args: {args}" if args else ""
    logger.info(f"🔧 TOOL CALL: {tool_name}{args_str}")


def log_tool_result(
    logger: logging.Logger, tool_name: str, result: Any = None
):
    """Log a tool result with standardized format."""
    result_str = f" -> {result}" if result else ""
    logger.info(f"✅ TOOL RESULT: {tool_name}{result_str}")
