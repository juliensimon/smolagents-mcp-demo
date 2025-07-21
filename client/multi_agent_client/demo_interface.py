#!/usr/bin/env python3
"""
Demo script for the improved Multi-Agent MCP Client interface.

This script launches the interface with improved styling and organization.
"""

import os
import sys
from pathlib import Path

from client.multi_agent_client.client import create_interface

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Launch the improved multi-agent interface."""

    print("🚀 Launching Multi-Agent Code Analysis Platform")
    print("=" * 50)

    # Check environment
    if not os.getenv("TOGETHER_API_KEY"):
        print("❌ TOGETHER_API_KEY environment variable not set!")
        print(
            "Please set it with: export TOGETHER_API_KEY='your_api_key_here'"
        )
        return

    print("✅ Environment check passed")
    print("🔌 Connecting to MCP servers...")

    # Create interface
    demo = create_interface()

    if demo:
        print("✅ Interface created successfully!")
        print("📋 Features:")
        print("  - Clean, organized text layout")
        print("  - Structured status tables")
        print("  - System overview metrics")
        print("  - Enhanced Agent Status page")
        print("  - Test connection functionality")
        print("  - System information display")
        print()
        print("🌐 Launching interface...")
        print("📱 Open your browser to access the interface")
        print("🔄 Use the Agent Status tab to monitor system health")

        # Launch the interface
        demo.launch(
            server_name="127.0.0.1",
            server_port=7864,
            share=False,
            show_error=True,
        )
    else:
        print("❌ Failed to create interface")


if __name__ == "__main__":
    main()
