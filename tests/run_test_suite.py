#!/usr/bin/env python3
"""
Simple Test Suite Runner

This script provides a user-friendly interface for running the MCP test suite.
It guides users to choose the appropriate test type based on their needs.
"""

import os
import subprocess
import sys
from pathlib import Path


def print_banner():
    """Print the test suite banner."""
    print("🚀 MCP Server Test Suite")
    print("=" * 50)
    print()


def print_test_options():
    """Print available test options."""
    print("Available Test Options:")
    print()
    print("📁 OFFLINE TESTS (Safe for CI/CD):")
    print("  quick     - Fast validation (config + environment)")
    print("  offline   - All offline tests")
    print()
    print("🌐 ONLINE TESTS (Require live servers):")
    print("  health    - Server health checks")
    print("  functionality - All server functionality")
    print("  integration   - Core integration tests")
    print("  online    - All online tests")
    print()
    print("🔧 UTILITY COMMANDS:")
    print("  all       - Complete test suite (offline + online)")
    print("  validate  - Environment validation")
    print("  list      - List all test categories")
    print("  help      - Show this help")
    print()


def check_environment():
    """Check if environment is ready for online tests."""
    issues = []

    # Check API key
    if not os.getenv("TOGETHER_API_KEY"):
        issues.append("TOGETHER_API_KEY environment variable not set")

    # Check if servers are accessible by testing their URLs
    try:
        from config_loader import get_config_loader

        config_loader = get_config_loader()
        servers = config_loader.get_servers()

        import requests

        for server_key, server_config in servers.items():
            try:
                # Test the server URL with a short timeout
                response = requests.get(server_config["url"], timeout=2)
                if response.status_code != 200:
                    issues.append(
                        f"Server {server_config['name']} returned status {response.status_code}"
                    )
            except requests.exceptions.RequestException as e:
                issues.append(
                    f"Server {server_config['name']} not accessible: {str(e)}"
                )
    except ImportError:
        # Fallback to port checking if config_loader is not available
        server_ports = [7860, 7862, 7865, 7866, 7867]
        import socket

        for port in server_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", port))
                sock.close()
                if result != 0:
                    issues.append(f"Server on port {port} not accessible")
            except:
                issues.append(f"Could not check port {port}")

    return issues


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def main():
    """Main function."""
    print_banner()

    if len(sys.argv) < 2:
        print("Usage: python run_test_suite.py <test_type> [options]")
        print()
        print_test_options()
        return

    test_type = sys.argv[1].lower()

    if test_type in ["help", "-h", "--help"]:
        print_test_options()
        return

    # Define test commands
    test_commands = {
        "quick": ["python", "run_tests.py", "quick"],
        "offline": ["python", "run_tests.py", "offline"],
        "health": ["python", "run_tests.py", "health"],
        "functionality": ["python", "run_tests.py", "functionality"],
        "integration": ["python", "run_tests.py", "integration"],
        "online": ["python", "run_tests.py", "online"],
        "all": ["python", "run_tests.py", "all"],
        "validate": ["python", "run_tests.py", "validate"],
        "list": ["python", "run_tests.py", "list-categories"],
    }

    if test_type not in test_commands:
        print(f"❌ Unknown test type: {test_type}")
        print()
        print_test_options()
        sys.exit(1)

    # Add verbose flag if requested
    cmd = test_commands[test_type]
    if "--verbose" in sys.argv or "-v" in sys.argv:
        cmd.append("--verbose")

    # Add report flag if requested
    if "--report" in sys.argv:
        cmd.append("--report")

    # Check environment for online tests
    if test_type in [
        "health",
        "functionality",
        "integration",
        "online",
        "all",
    ]:
        print("🔍 Checking environment for online tests...")
        issues = check_environment()

        if issues:
            print("⚠️  Environment issues detected:")
            for issue in issues:
                print(f"   - {issue}")
            print()

            if test_type == "all":
                print("🔄 Falling back to offline-only tests...")
                cmd = ["python", "run_tests.py", "offline", "--offline-only"]
                if "--verbose" in sys.argv or "-v" in sys.argv:
                    cmd.append("--verbose")
                if "--report" in sys.argv:
                    cmd.append("--report")
            else:
                print("❌ Cannot run online tests with current environment.")
                print("   Please:")
                print("   1. Set TOGETHER_API_KEY environment variable")
                print(
                    "   2. Start all MCP servers: python start_all_servers.py"
                )
                print(
                    "   3. Try running offline tests first: python run_test_suite.py offline"
                )
                sys.exit(1)

    # Run the test command
    success = run_command(cmd, f"{test_type.title()} Tests")

    if success:
        print("\n🎉 Test execution completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test execution failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
