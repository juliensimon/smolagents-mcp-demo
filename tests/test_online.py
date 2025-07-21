#!/usr/bin/env python3
"""
Online Tests - Tests that require live MCP servers and endpoints

These tests require all MCP servers to be running and external endpoints to be available.
They should NOT be run in CI environments where servers are not available.
"""

import os
import sys
import time
import unittest

# Add the parent directory to the path so we can import from tests
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from smolagents import MCPClient, OpenAIServerModel, ToolCallingAgent

from config_loader import get_config_loader


class TestMCPIntegrationOnline(unittest.TestCase):
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


class TestServerHealthOnline(unittest.TestCase):
    """Test server health and connectivity."""

    def setUp(self):
        """Set up test environment."""
        self.config_loader = get_config_loader()
        self.servers = self.config_loader.get_servers()

    def test_server_health_checks(self):
        """Test that all servers are responding to health checks."""
        for server_key, server_config in self.servers.items():
            with self.subTest(server=server_key):
                try:
                    # Use MCP client to test server health
                    client = MCPClient({"url": server_config["url"]})
                    tools = client.get_tools()
                    self.assertGreater(
                        len(tools), 0, f"Server {server_key} has no tools"
                    )
                    client.disconnect()
                except Exception as e:
                    self.fail(f"Server {server_key} health check failed: {e}")

    def test_mcp_endpoints_accessible(self):
        """Test that MCP endpoints are accessible."""
        for server_key, server_config in self.servers.items():
            with self.subTest(server=server_key):
                try:
                    client = MCPClient({"url": server_config["url"]})
                    tools = client.get_tools()
                    self.assertGreater(
                        len(tools), 0, f"No tools from {server_key}"
                    )
                    client.disconnect()
                except Exception as e:
                    self.fail(f"MCP endpoint {server_key} not accessible: {e}")

    def test_server_response_times(self):
        """Test that servers respond within reasonable time."""
        for server_key, server_config in self.servers.items():
            with self.subTest(server=server_key):
                start_time = time.time()
                try:
                    # Use MCP client to test response time
                    client = MCPClient({"url": server_config["url"]})
                    tools = client.get_tools()
                    end_time = time.time()
                    response_time = end_time - start_time

                    self.assertLess(
                        response_time,
                        10.0,
                        f"Server {server_key} too slow: {response_time:.2f}s",
                    )
                    self.assertGreater(
                        len(tools), 0, f"Server {server_key} has no tools"
                    )
                    client.disconnect()
                except Exception as e:
                    self.fail(
                        f"Server {server_key} response time test failed: {e}"
                    )


class TestBasicServerFunctionalityOnline(unittest.TestCase):
    """Test basic server functionality in detail."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.config_loader = get_config_loader()
        cls.server_config = cls.config_loader.get_server_config("basic_server")
        cls.model_config = cls.config_loader.get_model_config()

        try:
            client = MCPClient({"url": cls.server_config["url"]})
            cls.mcp_client = client

            tools = client.get_tools()

            model = OpenAIServerModel(
                model_id=cls.model_config["default"],
                api_base=cls.model_config["api_base"],
                api_key=os.getenv("TOGETHER_API_KEY"),
                **cls.config_loader.get_model_params(),
            )

            cls.agent = ToolCallingAgent(tools=tools, model=model)

        except Exception as e:
            print(f"Failed to connect to basic server: {e}")
            cls.mcp_client = None
            cls.agent = None

    def test_sentiment_analysis_positive(self):
        """Test sentiment analysis with positive text."""
        if not self.agent:
            self.skipTest("Basic server not available")

        test_cases = [
            "I love this product! It's absolutely amazing.",
            "This is the best experience I've ever had.",
            "Fantastic service and wonderful support!",
            "I'm so happy with the results!",
            "Excellent quality and great value for money.",
        ]

        for text in test_cases:
            with self.subTest(text=text[:30] + "..."):
                response = self.agent.run(
                    f"Analyze the sentiment of this text: {text}"
                )
                self.assertIsNotNone(response)
                self.assertIn("sentiment", str(response).lower())

    def test_sentiment_analysis_negative(self):
        """Test sentiment analysis with negative text."""
        if not self.agent:
            self.skipTest("Basic server not available")

        test_cases = [
            "I hate this product. It's terrible.",
            "This is the worst experience ever.",
            "Terrible service and poor quality.",
            "I'm very disappointed with the results.",
            "Awful customer support and bad product.",
        ]

        for text in test_cases:
            with self.subTest(text=text[:30] + "..."):
                response = self.agent.run(
                    f"Analyze the sentiment of this text: {text}"
                )
                self.assertIsNotNone(response)
                self.assertIn("sentiment", str(response).lower())


class TestCodeMetricsServerFunctionalityOnline(unittest.TestCase):
    """Test code metrics server functionality in detail."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.config_loader = get_config_loader()
        cls.server_config = cls.config_loader.get_server_config("code_metrics")
        cls.model_config = cls.config_loader.get_model_config()

        try:
            client = MCPClient({"url": cls.server_config["url"]})
            cls.mcp_client = client

            tools = client.get_tools()

            model = OpenAIServerModel(
                model_id=cls.model_config["default"],
                api_base=cls.model_config["api_base"],
                api_key=os.getenv("TOGETHER_API_KEY"),
                **cls.config_loader.get_model_params(),
            )

            cls.agent = ToolCallingAgent(tools=tools, model=model)

        except Exception as e:
            print(f"Failed to connect to code metrics server: {e}")
            cls.mcp_client = None
            cls.agent = None

    def test_complexity_analysis_simple(self):
        """Test complexity analysis with simple code."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        test_code = """
def add(a, b):
    return a + b
"""
        response = self.agent.run(
            f"Calculate the complexity of this code: {test_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("complexity", str(response).lower())

    def test_style_analysis(self):
        """Test code style analysis."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        test_code = """
def bad_style_function( x,y ):
    z=x+y
    return z
"""
        response = self.agent.run(
            f"Analyze the style of this code: {test_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("style", str(response).lower())


class TestCodeSecurityServerFunctionalityOnline(unittest.TestCase):
    """Test code security server functionality in detail."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.config_loader = get_config_loader()
        cls.server_config = cls.config_loader.get_server_config(
            "code_security"
        )
        cls.model_config = cls.config_loader.get_model_config()

        try:
            client = MCPClient({"url": cls.server_config["url"]})
            cls.mcp_client = client

            tools = client.get_tools()

            model = OpenAIServerModel(
                model_id=cls.model_config["default"],
                api_base=cls.model_config["api_base"],
                api_key=os.getenv("TOGETHER_API_KEY"),
                **cls.config_loader.get_model_params(),
            )

            cls.agent = ToolCallingAgent(tools=tools, model=model)

        except Exception as e:
            print(f"Failed to connect to code security server: {e}")
            cls.mcp_client = None
            cls.agent = None

    def test_sql_injection_detection(self):
        """Test SQL injection vulnerability detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        vulnerable_code = """
import sqlite3
def vulnerable_query(user_input):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor.execute(query)
    return cursor.fetchall()
"""
        response = self.agent.run(
            f"Check this code for SQL injection vulnerabilities: {vulnerable_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("sql", str(response).lower())

    def test_command_injection_detection(self):
        """Test command injection vulnerability detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        vulnerable_code = """
import os
def dangerous_function(user_input):
    os.system(user_input)
"""
        response = self.agent.run(
            f"Check this code for command injection vulnerabilities: {vulnerable_code}"
        )
        self.assertIsNotNone(response)
        self.assertIn("command", str(response).lower())


class TestCodeRetrievalServerFunctionalityOnline(unittest.TestCase):
    """Test code retrieval server functionality in detail."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.config_loader = get_config_loader()
        cls.server_config = cls.config_loader.get_server_config(
            "code_retrieval"
        )
        cls.model_config = cls.config_loader.get_model_config()

        try:
            client = MCPClient({"url": cls.server_config["url"]})
            cls.mcp_client = client

            tools = client.get_tools()

            model = OpenAIServerModel(
                model_id=cls.model_config["default"],
                api_base=cls.model_config["api_base"],
                api_key=os.getenv("TOGETHER_API_KEY"),
                **cls.config_loader.get_model_params(),
            )

            cls.agent = ToolCallingAgent(tools=tools, model=model)

        except Exception as e:
            print(f"Failed to connect to code retrieval server: {e}")
            cls.mcp_client = None
            cls.agent = None

    def test_url_validation_valid(self):
        """Test URL validation with valid URLs."""
        if not self.agent:
            self.skipTest("Code retrieval server not available")

        valid_urls = [
            "https://httpbin.org/json",
            "https://api.github.com/users/octocat",
            "https://jsonplaceholder.typicode.com/posts/1",
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                response = self.agent.run(f"Validate this URL: {url}")
                self.assertIsNotNone(response)
                self.assertIn("valid", str(response).lower())

    def test_content_retrieval(self):
        """Test content retrieval from URLs."""
        if not self.agent:
            self.skipTest("Code retrieval server not available")

        test_url = "https://httpbin.org/json"
        response = self.agent.run(
            f"Retrieve content from this URL: {test_url}"
        )
        self.assertIsNotNone(response)
        # Check that we got a response (the actual content is JSON data)
        self.assertGreater(len(str(response)), 0)


class TestGitServerFunctionalityOnline(unittest.TestCase):
    """Test git server functionality in detail."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.config_loader = get_config_loader()
        cls.server_config = cls.config_loader.get_server_config(
            "git_repo_analysis"
        )
        cls.model_config = cls.config_loader.get_model_config()

        try:
            client = MCPClient({"url": cls.server_config["url"]})
            cls.mcp_client = client

            tools = client.get_tools()

            model = OpenAIServerModel(
                model_id=cls.model_config["default"],
                api_base=cls.model_config["api_base"],
                api_key=os.getenv("TOGETHER_API_KEY"),
                **cls.config_loader.get_model_params(),
            )

            cls.agent = ToolCallingAgent(tools=tools, model=model)

        except Exception as e:
            print(f"Failed to connect to git server: {e}")
            cls.mcp_client = None
            cls.agent = None

    def test_git_status(self):
        """Test git status functionality."""
        if not self.agent:
            self.skipTest("Git server not available")

        # Get the project root directory (parent of tests directory)
        project_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        response = self.agent.run(
            f"Get the git status of the repository at {project_root}"
        )
        self.assertIsNotNone(response)
        # Check that we got a response about git status
        response_str = str(response).lower()
        self.assertTrue(
            "status" in response_str
            or "git" in response_str
            or "branch" in response_str,
            f"Expected git status information, got: {response_str}",
        )

    def test_git_log(self):
        """Test git log functionality."""
        if not self.agent:
            self.skipTest("Git server not available")

        # Get the project root directory (parent of tests directory)
        project_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        response = self.agent.run(
            f"Get the recent git log for the repository at {project_root}"
        )
        self.assertIsNotNone(response)
        # Check that we got a response about git log
        response_str = str(response).lower()
        self.assertTrue(
            "log" in response_str
            or "git" in response_str
            or "commit" in response_str,
            f"Expected git log information, got: {response_str}",
        )


class TestIntegrationScenariosOnline(unittest.TestCase):
    """Test complex integration scenarios and workflows."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment with all agents."""
        cls.config_loader = get_config_loader()
        cls.servers = cls.config_loader.get_servers()
        cls.model_config = cls.config_loader.get_model_config()

        # Create agents for each server
        cls.agents = {}

        for server_key, server_config in cls.servers.items():
            try:
                client = MCPClient({"url": server_config["url"]})
                tools = client.get_tools()

                model = OpenAIServerModel(
                    model_id=cls.model_config["default"],
                    api_base=cls.model_config["api_base"],
                    api_key=os.getenv("TOGETHER_API_KEY"),
                    **cls.config_loader.get_model_params(),
                )

                agent = ToolCallingAgent(tools=tools, model=model)
                cls.agents[server_key] = agent

            except Exception as e:
                print(f"Failed to connect to {server_config['name']}: {e}")
                cls.agents[server_key] = None

    def test_code_review_workflow(self):
        """Test a complete code review workflow."""
        if not all(self.agents.values()):
            self.skipTest("Not all servers available")

        # This would test a complex workflow involving multiple servers
        # For now, just test that we can access the agents
        self.assertGreater(len(self.agents), 0)
        for server_key, agent in self.agents.items():
            if agent:
                self.assertIsNotNone(agent)

    def test_continuous_integration_workflow(self):
        """Test a CI workflow scenario."""
        if not all(self.agents.values()):
            self.skipTest("Not all servers available")

        # This would test a CI workflow
        # For now, just test that we can access the agents
        self.assertGreater(len(self.agents), 0)


if __name__ == "__main__":
    unittest.main()
