"""
MCP Git Server

A Model Context Protocol server that provides basic git operations
for local files including status, add, commit, diff, and log.
"""

from .git_server import git_add, git_commit, git_diff, git_log, git_status

__version__ = "1.0.0"
__author__ = "MCP Demo Team"

__all__ = ["git_status", "git_add", "git_commit", "git_diff", "git_log"]
