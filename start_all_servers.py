#!/usr/bin/env python3
"""
Script to start all Gradio MCP servers and run integration tests
"""

import os
import subprocess
import sys
import time
from typing import Dict

import requests

from config_loader import get_config_loader

# Add the project root to the path to import config_loader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ServerManager:
    """Manages starting and stopping all Gradio MCP servers."""

    def __init__(self):
        self.config_loader = get_config_loader()
        self.servers = self.config_loader.get_servers()
        self.processes = {}

    def start_server(self, server_key: str) -> bool:
        """Start a specific server."""
        if server_key not in self.servers:
            print(f"❌ Unknown server: {server_key}")
            return False

        server_config = self.servers[server_key]
        server_path = server_config["path"]

        if not os.path.exists(server_path):
            print(f"❌ Server file not found: {server_path}")
            return False

        try:
            print(
                f"🚀 Starting {server_config['name']} on port {server_config['port']}..."
            )
            process = subprocess.Popen(
                [sys.executable, server_path],
                stdout=None,  # Use parent's stdout to see output on screen
                stderr=None,  # Use parent's stderr to see errors on screen
                text=True,
            )

            self.processes[server_key] = process

            # Wait a bit for the server to start
            startup_wait = self.config_loader.get_testing_config().get(
                "startup_wait_time", 3
            )
            time.sleep(startup_wait)

            # Check if server is responding
            if self.check_server_health(server_key):
                print(f"✅ {server_config['name']} started successfully")
                return True
            else:
                print(f"❌ {server_config['name']} failed to start")
                return False

        except Exception as e:
            print(f"❌ Error starting {server_config['name']}: {e}")
            return False

    def check_server_health(self, server_key: str) -> bool:
        """Check if a server is responding."""
        if server_key not in self.servers:
            return False

        server_config = self.servers[server_key]
        port = server_config["port"]

        try:
            health_check_interval = self.config_loader.get_testing_config().get(
                "health_check_interval", 5
            )
            response = requests.get(
                f"http://localhost:{port}", timeout=health_check_interval
            )
            return response.status_code == 200
        except Exception:
            return False

    def start_all_servers(self) -> Dict[str, bool]:
        """Start all servers."""
        print("🚀 Starting all MCP servers...")
        print("=" * 50)

        results = {}
        for server_key in self.servers:
            results[server_key] = self.start_server(server_key)

        return results

    def stop_server(self, server_key: str):
        """Stop a specific server."""
        if server_key in self.processes:
            try:
                self.processes[server_key].terminate()
                self.processes[server_key].wait(timeout=5)
                print(f"🛑 Stopped {self.servers[server_key]['name']}")
            except subprocess.TimeoutExpired:
                self.processes[server_key].kill()
                print(f"🛑 Force killed {self.servers[server_key]['name']}")
            except Exception as e:
                print(f"❌ Error stopping {server_key}: {e}")

    def stop_all_servers(self):
        """Stop all servers."""
        print("🛑 Stopping all servers...")
        for server_key in list(self.processes.keys()):
            self.stop_server(server_key)

    def get_server_status(self) -> Dict[str, bool]:
        """Get status of all servers."""
        status = {}
        for server_key in self.servers:
            status[server_key] = self.check_server_health(server_key)
        return status


class IntegrationTester:
    """Runs integration tests against the MCP servers."""

    def __init__(self, server_manager: ServerManager):
        self.server_manager = server_manager
        self.config_loader = get_config_loader()

    def test_code_retrieval_server(self) -> bool:
        """Test code retrieval server functionality."""
        server_key = "code_retrieval"
        if not self.server_manager.check_server_health(server_key):
            print(f"❌ {server_key} server not responding")
            return False

        server_config = self.server_manager.servers[server_key]
        port = server_config["port"]

        try:
            # Test basic connectivity
            response = requests.get(f"http://localhost:{port}", timeout=10)
            if response.status_code != 200:
                print(f"❌ {server_key} server returned status {response.status_code}")
                return False

            print(f"✅ {server_key} server is responding")
            return True

        except Exception as e:
            print(f"❌ Error testing {server_key} server: {e}")
            return False

    def test_code_metrics_server(self) -> bool:
        """Test code metrics server functionality."""
        server_key = "code_metrics"
        if not self.server_manager.check_server_health(server_key):
            print(f"❌ {server_key} server not responding")
            return False

        server_config = self.server_manager.servers[server_key]
        port = server_config["port"]

        try:
            # Test basic connectivity
            response = requests.get(f"http://localhost:{port}", timeout=10)
            if response.status_code != 200:
                print(f"❌ {server_key} server returned status {response.status_code}")
                return False

            print(f"✅ {server_key} server is responding")
            return True

        except Exception as e:
            print(f"❌ Error testing {server_key} server: {e}")
            return False

    def test_code_security_server(self) -> bool:
        """Test code security server functionality."""
        server_key = "code_security"
        if not self.server_manager.check_server_health(server_key):
            print(f"❌ {server_key} server not responding")
            return False

        server_config = self.server_manager.servers[server_key]
        port = server_config["port"]

        try:
            # Test basic connectivity
            response = requests.get(f"http://localhost:{port}", timeout=10)
            if response.status_code != 200:
                print(f"❌ {server_key} server returned status {response.status_code}")
                return False

            print(f"✅ {server_key} server is responding")
            return True

        except Exception as e:
            print(f"❌ Error testing {server_key} server: {e}")
            return False

    def test_git_server(self) -> bool:
        """Test git server functionality."""
        server_key = "git_repo_analysis"
        if not self.server_manager.check_server_health(server_key):
            print(f"❌ {server_key} server not responding")
            return False

        server_config = self.server_manager.servers[server_key]
        port = server_config["port"]

        try:
            # Test basic connectivity
            response = requests.get(f"http://localhost:{port}", timeout=10)
            if response.status_code != 200:
                print(f"❌ {server_key} server returned status {response.status_code}")
                return False

            print(f"✅ {server_key} server is responding")
            return True

        except Exception as e:
            print(f"❌ Error testing {server_key} server: {e}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests."""
        print("🧪 Running integration tests...")
        print("=" * 50)

        tests = {
            "code_retrieval": self.test_code_retrieval_server,
            "code_metrics": self.test_code_metrics_server,
            "code_security": self.test_code_security_server,
            "git_repo_analysis": self.test_git_server,
        }

        results = {}
        for test_name, test_func in tests.items():
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ Error running {test_name} test: {e}")
                results[test_name] = False

        return results


def main():
    """Main function to start servers and run tests."""
    print("🚀 MCP Demo Server Manager")
    print("=" * 50)

    # Validate configuration
    config_loader = get_config_loader()
    if not config_loader.validate_config():
        print("❌ Configuration validation failed")
        sys.exit(1)

    print("✅ Configuration is valid")
    print(f"Available servers: {list(config_loader.get_servers().keys())}")

    # Create server manager
    server_manager = ServerManager()

    try:
        # Start all servers
        start_results = server_manager.start_all_servers()

        # Check if all servers started successfully
        if not all(start_results.values()):
            print("❌ Some servers failed to start")
            failed_servers = [
                key for key, success in start_results.items() if not success
            ]
            print(f"Failed servers: {failed_servers}")
            sys.exit(1)

        print("✅ All servers started successfully")
        print("\n🔄 Servers are running. Press Ctrl+C to stop all servers...")

        # Keep servers running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Always stop servers
        server_manager.stop_all_servers()


if __name__ == "__main__":
    main()
