#!/usr/bin/env python3
"""
Test script for the Multi-Agent MCP Client

This script demonstrates the multi-agent system functionality.
"""

import os
import sys
from pathlib import Path

from client.multi_agent_client.client import (
    disconnect,
    get_status,
    manager,
    setup_agents,
    setup_connections,
    setup_manager,
)

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_multi_agent_system():
    """Test the multi-agent system with different types of requests."""

    print("🚀 Testing Multi-Agent MCP Client")
    print("=" * 50)

    # Initialize the system
    setup_connections()
    setup_agents()
    setup_manager()

    # Test cases
    test_cases = [
        {
            "name": "Security Analysis",
            "request": "Please analyze this code for security vulnerabilities: import sqlite3; conn = sqlite3.connect('users.db'); cursor = conn.execute(f\"SELECT * FROM users WHERE username='{user_input}'\");",
            "expected_agent": "code_analysis_agent",
        },
        {
            "name": "Code Metrics",
            "request": "Please analyze this code for complexity and maintainability: def complex_function(x): return sum([i**2 for i in range(x) if i % 2 == 0])",
            "expected_agent": "code_analysis_agent",
        },
        {
            "name": "Code Search",
            "request": "Please search for authentication patterns and similar implementations",
            "expected_agent": "research_agent",
        },
        {
            "name": "Git Analysis",
            "request": "Please analyze the git repository structure and commit patterns",
            "expected_agent": "research_agent",
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"Request: {test_case['request'][:100]}...")
        print(f"Expected Agent: {test_case['expected_agent']}")

        try:
            # Check if manager is available
            if not manager:
                print("❌ Manager agent not initialized")
                continue

            # Run the analysis directly
            result = manager.run(test_case["request"])

            # Check if the result contains expected content
            if result and not str(result).startswith("❌"):
                print("✅ Analysis completed successfully")
                print(f"Result preview: {str(result)[:200]}...")
            else:
                print("⚠️ Analysis completed with issues")
                print(f"Result: {result}")

        except Exception as e:
            print(f"❌ Test failed: {e}")

    print("\n" + "=" * 50)
    print("🎯 Multi-Agent System Test Complete!")

    # Display agent status
    print("\n📊 Agent Status:")
    print(get_status())

    # Clean up
    disconnect()


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("TOGETHER_API_KEY"):
        print("❌ TOGETHER_API_KEY environment variable not set!")
        print("Please set it with: export TOGETHER_API_KEY='your_api_key_here'")
        exit(1)

    test_multi_agent_system()
