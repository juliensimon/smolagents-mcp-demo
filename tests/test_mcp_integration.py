#!/usr/bin/env python3
"""
Comprehensive MCP Integration Test Suite

This test suite tests real MCP server integration using actual MCP clients.
It assumes all MCP servers are running and the Together AI endpoint is live.
"""

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

import requests
from smolagents import MCPClient, OpenAIServerModel, ToolCallingAgent

from config_loader import get_config_loader

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMCPIntegration(unittest.TestCase):
    """Test real MCP server integration."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment with real MCP clients."""
        cls.config_loader = get_config_loader()
        cls.servers = cls.config_loader.get_servers()
        cls.model_config = cls.config_loader.get_model_config()

        # Create MCP clients for each server
        cls.mcp_clients = {}
        cls.tool_agents = {}

        for server_key, server_config in cls.servers.items():
            try:
                # Create MCP client
                client = MCPClient({"url": server_config["url"]})
                cls.mcp_clients[server_key] = client

                # Get tools from server
                tools = client.get_tools()

                # Create model
                model = OpenAIServerModel(
                    model_id=cls.model_config["default"],
                    api_base=cls.model_config["api_base"],
                    api_key=os.getenv("TOGETHER_API_KEY"),
                    **cls.config_loader.get_model_params(),
                )

                # Create tool calling agent
                agent = ToolCallingAgent(tools=tools, model=model)
                cls.tool_agents[server_key] = agent

                print(
                    f"✅ Connected to {server_config['name']} ({len(tools)} tools)"
                )

            except Exception as e:
                print(f"❌ Failed to connect to {server_config['name']}: {e}")
                cls.mcp_clients[server_key] = None
                cls.tool_agents[server_key] = None

    @classmethod
    def tearDownClass(cls):
        """Clean up MCP clients."""
        for client in cls.mcp_clients.values():
            if client:
                try:
                    client.disconnect()
                except Exception:
                    pass

    def test_server_connectivity(self):
        """Test that all servers are accessible."""
        for server_key, server_config in self.servers.items():
            with self.subTest(server=server_key):
                self.assertIsNotNone(
                    self.mcp_clients[server_key],
                    f"Failed to connect to {server_config['name']}",
                )

    def test_tools_availability(self):
        """Test that each server provides tools."""
        for server_key, server_config in self.servers.items():
            with self.subTest(server=server_key):
                if self.mcp_clients[server_key]:
                    tools = self.mcp_clients[server_key].get_tools()
                    self.assertGreater(
                        len(tools),
                        0,
                        f"No tools available from {server_config['name']}",
                    )
                    print(f"  {server_config['name']}: {len(tools)} tools")

    def test_basic_server_sentiment_analysis(self):
        """Test basic server sentiment analysis functionality."""
        if not self.tool_agents.get("basic_server"):
            self.skipTest("Basic server not available")

        agent = self.tool_agents["basic_server"]

        # Test positive sentiment
        positive_text = "I love this product! It's absolutely amazing."
        response = agent.run(
            f"Analyze the sentiment of this text: {positive_text}"
        )
        self.assertIsNotNone(response)
        self.assertIn("sentiment", str(response).lower())

        # Test negative sentiment
        negative_text = "This is terrible. I hate it."
        response = agent.run(
            f"Analyze the sentiment of this text: {negative_text}"
        )
        self.assertIsNotNone(response)
        self.assertIn("sentiment", str(response).lower())

        # Test neutral sentiment
        neutral_text = "The weather is cloudy today."
        response = agent.run(
            f"Analyze the sentiment of this text: {neutral_text}"
        )
        self.assertIsNotNone(response)
        self.assertIn("sentiment", str(response).lower())

    def test_code_metrics_server_complexity_analysis(self):
        """Test code metrics server complexity analysis."""
        if not self.tool_agents.get("code_metrics"):
            self.skipTest("Code Metrics server not available")

        agent = self.tool_agents["code_metrics"]

        # Test simple function
        simple_code = """
def hello():
    print("Hello, World!")
"""
        response = agent.run(
            f"Calculate the complexity of this code: {simple_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("complexity", str(response).lower())

        # Test complex function
        complex_code = """
def fibonacci(n):
    if n <= 1:
        return n
    if n == 2:
        return 1
    if n % 2 == 0:
        return fibonacci(n-1) + fibonacci(n-2)
    else:
        return fibonacci(n-1) + fibonacci(n-2) + 1
"""
        response = agent.run(
            f"Calculate the complexity of this code: {complex_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("complexity", str(response).lower())

    def test_code_metrics_server_style_analysis(self):
        """Test code metrics server style analysis."""
        if not self.tool_agents.get("code_metrics"):
            self.skipTest("Code Metrics server not available")

        agent = self.tool_agents["code_metrics"]

        # Test code style analysis
        test_code = """
def bad_style_function( x,y ):
    z=x+y
    return z
"""
        response = agent.run(f"Analyze the style of this code: {test_code}")
        self.assertIsNotNone(response)
        self.assertIn("style", str(response).lower())

    def test_code_metrics_server_naming_conventions(self):
        """Test code metrics server naming conventions analysis."""
        if not self.tool_agents.get("code_metrics"):
            self.skipTest("Code Metrics server not available")

        agent = self.tool_agents["code_metrics"]

        # Test naming conventions
        test_code = """
def BadFunctionName():
    variable_name = "good"
    BAD_CONSTANT = "bad"
    return variable_name
"""
        response = agent.run(
            f"Analyze the naming conventions in this code: {test_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("naming", str(response).lower())

    def test_code_security_server_vulnerability_detection(self):
        """Test code security server vulnerability detection."""
        if not self.tool_agents.get("code_security"):
            self.skipTest("Code Security server not available")

        agent = self.tool_agents["code_security"]

        # Test dangerous code patterns
        dangerous_code = """
import os
def dangerous_function(user_input):
    os.system(user_input)  # Command injection
    eval(user_input)       # Code injection
    exec(user_input)       # Code injection
"""
        response = agent.run(
            f"Analyze this code for security vulnerabilities: {dangerous_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("vulnerability", str(response).lower())

        # Test safe code
        safe_code = """
def safe_function(user_input):
    # Sanitize input
    sanitized = user_input.strip()
    return f"Hello, {sanitized}!"
"""
        response = agent.run(
            f"Analyze this code for security vulnerabilities: {safe_code}"
        )
        self.assertIsNotNone(response)

    def test_code_security_server_sql_injection_detection(self):
        """Test code security server SQL injection detection."""
        if not self.tool_agents.get("code_security"):
            self.skipTest("Code Security server not available")

        agent = self.tool_agents["code_security"]

        # Test SQL injection vulnerable code
        sql_vulnerable_code = """
import sqlite3
def vulnerable_query(user_input):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor.execute(query)
    return cursor.fetchall()
"""
        response = agent.run(
            f"Analyze this code for SQL injection vulnerabilities: {sql_vulnerable_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("sql", str(response).lower())

    def test_code_retrieval_server_url_validation(self):
        """Test code retrieval server URL validation."""
        if not self.tool_agents.get("code_retrieval"):
            self.skipTest("Code Retrieval server not available")

        agent = self.tool_agents["code_retrieval"]

        # Test valid URL
        valid_url = "https://httpbin.org/json"
        response = agent.run(f"Validate this URL: {valid_url}")
        self.assertIsNotNone(response)
        self.assertIn("valid", str(response).lower())

        # Test invalid URL
        invalid_url = "not-a-valid-url"
        response = agent.run(f"Validate this URL: {invalid_url}")
        self.assertIsNotNone(response)

    def test_code_retrieval_server_content_retrieval(self):
        """Test code retrieval server content retrieval."""
        if not self.tool_agents.get("code_retrieval"):
            self.skipTest("Code Retrieval server not available")

        agent = self.tool_agents["code_retrieval"]

        # Test content retrieval from a public API
        test_url = "https://httpbin.org/json"
        response = agent.run(f"Retrieve content from: {test_url}")
        self.assertIsNotNone(response)

    def test_git_server_repository_analysis(self):
        """Test git server repository analysis."""
        if not self.tool_agents.get("git_repo_analysis"):
            self.skipTest("Git Repo Analysis server not available")

        agent = self.tool_agents["git_repo_analysis"]

        # Create a temporary git repository for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize git repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'Test User'")
            os.system(
                f"cd {temp_path} && git config user.email 'test@example.com'"
            )

            # Create test files
            test_file1 = temp_path / "test1.py"
            test_file1.write_text('print("Hello, World!")')

            test_file2 = temp_path / "test2.py"
            test_file2.write_text('def hello(): return "Hello"')

            # Add and commit files
            os.system(f"cd {temp_path} && git add .")
            os.system(f"cd {temp_path} && git commit -m 'Initial commit'")

            # Test git status
            response = agent.run(
                f"Get the git status of this repository: {temp_path}"
            )
            self.assertIsNotNone(response)
            self.assertIn("status", str(response).lower())

            # Test git log
            response = agent.run(
                f"Get the git log of this repository: {temp_path}"
            )
            self.assertIsNotNone(response)
            self.assertIn("log", str(response).lower())

    def test_git_server_branch_operations(self):
        """Test git server branch operations."""
        if not self.tool_agents.get("git_repo_analysis"):
            self.skipTest("Git Repo Analysis server not available")

        agent = self.tool_agents["git_repo_analysis"]

        # Create a temporary git repository for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize git repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'Test User'")
            os.system(
                f"cd {temp_path} && git config user.email 'test@example.com'"
            )

            # Create initial file
            test_file = temp_path / "main.py"
            test_file.write_text('print("Main branch")')

            # Add and commit
            os.system(f"cd {temp_path} && git add .")
            os.system(f"cd {temp_path} && git commit -m 'Main commit'")

            # Create and switch to feature branch
            os.system(f"cd {temp_path} && git checkout -b feature-branch")

            # Test branch listing
            response = agent.run(
                f"List all branches in this repository: {temp_path}"
            )
            self.assertIsNotNone(response)
            self.assertIn("branch", str(response).lower())

    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling for all servers."""
        for server_key, agent in self.tool_agents.items():
            if not agent:
                continue

            with self.subTest(server=server_key):
                # Test with empty input
                response = agent.run("")
                self.assertIsNotNone(response)

                # Test with very long input
                long_input = "x" * 10000
                response = agent.run(f"Analyze this: {long_input}")
                self.assertIsNotNone(response)

                # Test with special characters
                special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
                response = agent.run(f"Analyze this: {special_chars}")
                self.assertIsNotNone(response)

                # Test with unicode characters
                unicode_text = "Hello 世界 🌍"
                response = agent.run(f"Analyze this: {unicode_text}")
                self.assertIsNotNone(response)

    def test_performance_benchmarks(self):
        """Test performance of tool calls across all servers."""
        performance_results = {}

        for server_key, agent in self.tool_agents.items():
            if not agent:
                continue

            with self.subTest(server=server_key):
                # Test with standard input
                test_input = (
                    "This is a test input for performance measurement."
                )

                start_time = time.time()
                response = agent.run(f"Analyze this: {test_input}")
                end_time = time.time()

                response_time = end_time - start_time
                performance_results[server_key] = response_time

                self.assertIsNotNone(response)
                self.assertLess(
                    response_time,
                    60.0,
                    f"Response time too slow for {server_key}: {response_time:.2f}s",
                )

                print(f"  {server_key}: {response_time:.2f}s")

        # Log performance summary
        if performance_results:
            avg_time = sum(performance_results.values()) / len(
                performance_results
            )
            print(f"Average response time: {avg_time:.2f}s")

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import queue
        import threading

        if not self.tool_agents.get("code_metrics"):
            self.skipTest("Code Metrics server not available")

        agent = self.tool_agents["code_metrics"]

        test_codes = [
            "def func1(): pass",
            "def func2(): return 42",
            "def func3(): print('test')",
            "def func4(): x = 1; return x",
            "def func5(): return 'hello'",
        ]

        results = queue.Queue()

        def run_analysis(code, index):
            try:
                response = agent.run(f"Analyze this code: {code}")
                results.put((index, response, None))
            except Exception as e:
                results.put((index, None, e))

        # Start concurrent threads
        threads = []
        for i, code in enumerate(test_codes):
            thread = threading.Thread(target=run_analysis, args=(code, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect results
        responses = []
        errors = []
        while not results.empty():
            index, response, error = results.get()
            if error:
                errors.append((index, error))
            else:
                responses.append((index, response))

        self.assertEqual(
            len(responses),
            len(test_codes),
            f"Expected {len(test_codes)} responses, got {len(responses)}",
        )
        self.assertEqual(
            len(errors), 0, f"Got {len(errors)} errors in concurrent requests"
        )

    def test_end_to_end_workflow(self):
        """Test a complete end-to-end workflow."""
        if not all(self.tool_agents.values()):
            self.skipTest("Not all servers available")

        # Test workflow: retrieve code -> analyze metrics -> check security
        test_url = "https://raw.githubusercontent.com/python/cpython/main/Lib/collections/__init__.py"

        # Use code retrieval to get the file
        retrieval_agent = self.tool_agents["code_retrieval"]
        retrieval_response = retrieval_agent.run(
            f"Retrieve the content from: {test_url}"
        )
        self.assertIsNotNone(retrieval_response)

        # Use code metrics to analyze the retrieved code
        metrics_agent = self.tool_agents["code_metrics"]
        metrics_response = metrics_agent.run(
            f"Analyze the complexity of this code: {retrieval_response}"
        )
        self.assertIsNotNone(metrics_response)

        # Use code security to check for vulnerabilities
        security_agent = self.tool_agents["code_security"]
        security_response = security_agent.run(
            f"Check this code for security vulnerabilities: {retrieval_response}"
        )
        self.assertIsNotNone(security_response)

    def test_data_consistency(self):
        """Test that responses are consistent across multiple calls."""
        if not self.tool_agents.get("basic_server"):
            self.skipTest("Basic server not available")

        agent = self.tool_agents["basic_server"]
        test_text = "I love this product! It's absolutely amazing."

        # Make multiple calls with the same input
        responses = []
        for _ in range(3):
            response = agent.run(
                f"Analyze the sentiment of this text: {test_text}"
            )
            responses.append(response)
            time.sleep(1)  # Small delay between calls

        # All responses should be valid
        for response in responses:
            self.assertIsNotNone(response)
            self.assertIn("sentiment", str(response).lower())

    def test_memory_usage(self):
        """Test memory usage during tool calls."""
        import os

        import psutil

        if not self.tool_agents.get("code_metrics"):
            self.skipTest("Code Metrics server not available")

        agent = self.tool_agents["code_metrics"]

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make several tool calls
        test_codes = [
            "def func1(): pass",
            "def func2(): return 42",
            "def func3(): print('test')",
            "def func4(): x = 1; return x",
            "def func5(): return 'hello'",
        ]

        for code in test_codes:
            response = agent.run(f"Analyze this code: {code}")
            self.assertIsNotNone(response)

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(
            memory_increase,
            100.0,
            f"Memory usage increased by {memory_increase:.2f}MB",
        )
        print(f"Memory usage increase: {memory_increase:.2f}MB")


class TestConfiguration(unittest.TestCase):
    """Test configuration validation and loading."""

    def test_config_structure(self):
        """Test that configuration has the correct structure."""
        config_loader = get_config_loader()
        config = config_loader.get_config()

        # Check required sections
        self.assertIn("servers", config)
        self.assertIn("model", config)
        self.assertIn("client", config)
        self.assertIn("testing", config)
        self.assertIn("logging", config)

        # Check server configurations
        for server_key, server_config in config["servers"].items():
            self.assertIn("name", server_config)
            self.assertIn("port", server_config)
            self.assertIn("url", server_config)
            self.assertIn("description", server_config)
            self.assertIn("path", server_config)

        # Check model configuration
        model_config = config["model"]
        self.assertIn("default", model_config)
        self.assertIn("api_base", model_config)
        self.assertIn("configs", model_config)

    def test_server_urls_valid(self):
        """Test that server URLs are valid."""
        config_loader = get_config_loader()

        for server_key, server_config in config_loader.get_servers().items():
            with self.subTest(server=server_key):
                url = server_config["url"]
                self.assertTrue(url.startswith("http://"))
                self.assertIn("gradio_api/mcp/sse", url)

    def test_server_ports_unique(self):
        """Test that server ports are unique."""
        config_loader = get_config_loader()
        servers = config_loader.get_servers()

        ports = [server["port"] for server in servers.values()]
        unique_ports = set(ports)

        self.assertEqual(
            len(ports), len(unique_ports), "Duplicate ports found"
        )

    def test_model_configuration(self):
        """Test that model configuration is complete."""
        config_loader = get_config_loader()
        model_config = config_loader.get_model_config()

        # Check default model exists
        default_model = model_config["default"]
        configs = model_config["configs"]
        self.assertIn(default_model, configs)

        # Check model parameters
        model_params = config_loader.get_model_params()
        required_params = [
            "temperature",
            "max_tokens",
            "top_p",
            "repetition_penalty",
            "system_prompt",
        ]

        for param in required_params:
            self.assertIn(param, model_params)

    def test_configuration_validation(self):
        """Test that configuration validation passes."""
        config_loader = get_config_loader()
        self.assertTrue(
            config_loader.validate_config(), "Configuration validation failed"
        )

    def test_server_paths_exist(self):
        """Test that server paths exist."""
        config_loader = get_config_loader()

        for server_key, server_config in config_loader.get_servers().items():
            with self.subTest(server=server_key):
                server_path = Path(server_config["path"])
                self.assertTrue(
                    server_path.exists(),
                    f"Server path does not exist: {server_path}",
                )


class TestEnvironment(unittest.TestCase):
    """Test environment setup and requirements."""

    def test_environment_variables(self):
        """Test that required environment variables are set."""
        api_key = os.getenv("TOGETHER_API_KEY")
        self.assertIsNotNone(
            api_key, "TOGETHER_API_KEY environment variable not set"
        )
        self.assertGreater(len(api_key), 0, "TOGETHER_API_KEY is empty")

    def test_dependencies_available(self):
        """Test that required dependencies are available."""
        try:
            # requests is already imported at the top of the file
            pass
        except ImportError as e:
            self.fail(f"Missing dependency: {e}")

    def test_configuration_validation(self):
        """Test that configuration validation passes."""
        config_loader = get_config_loader()
        self.assertTrue(
            config_loader.validate_config(), "Configuration validation failed"
        )

    def test_python_version(self):
        """Test that Python version is compatible."""
        import sys

        version = sys.version_info
        self.assertGreaterEqual(version.major, 3, "Python 3.x required")
        self.assertGreaterEqual(version.minor, 8, "Python 3.8+ required")


class TestServerHealth(unittest.TestCase):
    """Test server health and connectivity."""

    def test_server_health_checks(self):
        """Test that all servers are responding to health checks."""
        config_loader = get_config_loader()
        servers = config_loader.get_servers()

        for server_key, server_config in servers.items():
            with self.subTest(server=server_key):
                port = server_config["port"]

                try:
                    response = requests.get(
                        f"http://localhost:{port}", timeout=5
                    )
                    self.assertEqual(
                        response.status_code,
                        200,
                        f"Server {server_key} not responding",
                    )
                except requests.exceptions.RequestException as e:
                    self.fail(f"Server {server_key} health check failed: {e}")

    def test_mcp_endpoints_accessible(self):
        """Test that MCP endpoints are accessible."""
        config_loader = get_config_loader()
        servers = config_loader.get_servers()

        for server_key, server_config in servers.items():
            with self.subTest(server=server_key):
                mcp_url = server_config["url"]

                try:
                    response = requests.get(mcp_url, timeout=5)
                    # MCP endpoints might return different status codes, but should not be unreachable
                    self.assertNotEqual(
                        response.status_code,
                        404,
                        f"MCP endpoint {server_key} not found",
                    )
                except requests.exceptions.RequestException as e:
                    self.fail(f"MCP endpoint {server_key} not accessible: {e}")

    def test_server_response_times(self):
        """Test that servers respond within reasonable time."""
        config_loader = get_config_loader()
        servers = config_loader.get_servers()

        for server_key, server_config in servers.items():
            with self.subTest(server=server_key):
                port = server_config["port"]

                start_time = time.time()
                try:
                    response = requests.get(  # noqa: F841
                        f"http://localhost:{port}", timeout=10
                    )
                    end_time = time.time()

                    response_time = end_time - start_time
                    self.assertLess(
                        response_time,
                        5.0,
                        f"Server {server_key} response time too slow: {response_time:.2f}s",
                    )

                except requests.exceptions.RequestException as e:
                    self.fail(f"Server {server_key} health check failed: {e}")

    def test_server_stability(self):
        """Test server stability with multiple requests."""
        config_loader = get_config_loader()
        servers = config_loader.get_servers()

        for server_key, server_config in servers.items():
            with self.subTest(server=server_key):
                port = server_config["port"]

                # Make multiple requests to test stability
                for i in range(5):
                    try:
                        response = requests.get(
                            f"http://localhost:{port}", timeout=5
                        )
                        self.assertEqual(
                            response.status_code,
                            200,
                            f"Server {server_key} unstable on request {i + 1}",
                        )
                    except requests.exceptions.RequestException as e:
                        self.fail(
                            f"Server {server_key} failed on request {i + 1}: {e}"
                        )


class TestIntegrationScenarios(unittest.TestCase):
    """Test complex integration scenarios."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.config_loader = get_config_loader()
        cls.servers = cls.config_loader.get_servers()
        cls.model_config = cls.config_loader.get_model_config()

        # Create MCP clients
        cls.mcp_clients = {}
        cls.tool_agents = {}

        for server_key, server_config in cls.servers.items():
            try:
                client = MCPClient({"url": server_config["url"]})
                cls.mcp_clients[server_key] = client

                tools = client.get_tools()

                model = OpenAIServerModel(
                    model_id=cls.model_config["default"],
                    api_base=cls.model_config["api_base"],
                    api_key=os.getenv("TOGETHER_API_KEY"),
                    **cls.config_loader.get_model_params(),
                )

                agent = ToolCallingAgent(tools=tools, model=model)
                cls.tool_agents[server_key] = agent

            except Exception as e:
                print(f"Failed to connect to {server_config['name']}: {e}")
                cls.mcp_clients[server_key] = None
                cls.tool_agents[server_key] = None

    def test_code_review_workflow(self):
        """Test a complete code review workflow."""
        if not all(self.tool_agents.values()):
            self.skipTest("Not all servers available")

        # Simulate a code review workflow
        test_code = """
import os
def process_user_input(user_input):
    # This is dangerous code
    os.system(user_input)
    eval(user_input)
    return "processed"
"""

        # Step 1: Analyze code complexity
        metrics_agent = self.tool_agents["code_metrics"]
        complexity_response = metrics_agent.run(
            f"Analyze the complexity of this code: {test_code}"
        )
        self.assertIsNotNone(complexity_response)

        # Step 2: Check for security vulnerabilities
        security_agent = self.tool_agents["code_security"]
        security_response = security_agent.run(
            f"Analyze this code for security vulnerabilities: {test_code}"
        )
        self.assertIsNotNone(security_response)

        # Step 3: Analyze code style
        style_response = metrics_agent.run(
            f"Analyze the style of this code: {test_code}"
        )
        self.assertIsNotNone(style_response)

    def test_continuous_integration_workflow(self):
        """Test a CI/CD workflow simulation."""
        if not all(self.tool_agents.values()):
            self.skipTest("Not all servers available")

        # Simulate a CI/CD pipeline
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'CI Bot'")
            os.system(
                f"cd {temp_path} && git config user.email 'ci@example.com'"
            )

            # Create test code
            test_file = temp_path / "app.py"
            test_file.write_text(
                """
def calculate_sum(a, b):
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""
            )

            # Add and commit
            os.system(f"cd {temp_path} && git add .")
            os.system(f"cd {temp_path} && git commit -m 'Initial commit'")

            # Simulate CI checks
            git_agent = self.tool_agents["git_repo_analysis"]
            metrics_agent = self.tool_agents["code_metrics"]
            security_agent = self.tool_agents["code_security"]

            # Check git status
            git_response = git_agent.run(
                f"Get the git status of this repository: {temp_path}"
            )
            self.assertIsNotNone(git_response)

            # Analyze code metrics
            code_content = test_file.read_text()
            metrics_response = metrics_agent.run(
                f"Analyze the complexity of this code: {code_content}"
            )
            self.assertIsNotNone(metrics_response)

            # Check security
            security_response = security_agent.run(
                f"Analyze this code for security vulnerabilities: {code_content}"
            )
            self.assertIsNotNone(security_response)

    def test_multi_language_support(self):
        """Test support for multiple programming languages."""
        if not self.tool_agents.get("code_metrics"):
            self.skipTest("Code Metrics server not available")

        agent = self.tool_agents["code_metrics"]

        # Test Python code
        python_code = """
def python_function():
    return "Hello from Python"
"""
        response = agent.run(f"Analyze this Python code: {python_code}")
        self.assertIsNotNone(response)

        # Test JavaScript-like code
        js_code = """
function jsFunction() {
    return "Hello from JavaScript";
}
"""
        response = agent.run(f"Analyze this JavaScript code: {js_code}")
        self.assertIsNotNone(response)

    def test_large_codebase_analysis(self):
        """Test analysis of large codebases."""
        if not self.tool_agents.get("code_metrics"):
            self.skipTest("Code Metrics server not available")

        agent = self.tool_agents["code_metrics"]

        # Create a larger codebase
        large_code = """
class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history.clear()

def main():
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.subtract(10, 4))
    print(calc.multiply(6, 7))
    print(calc.divide(20, 5))
    print("History:", calc.get_history())

if __name__ == "__main__":
    main()
"""

        response = agent.run(
            f"Analyze the complexity of this large code: {large_code}"
        )
        self.assertIsNotNone(response)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestMCPIntegration,
        TestConfiguration,
        TestEnvironment,
        TestServerHealth,
        TestIntegrationScenarios,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
