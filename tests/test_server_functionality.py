#!/usr/bin/env python3
"""
Detailed Server Functionality Tests

This test suite focuses on testing individual server functionalities in detail,
including specific tool calls, edge cases, and error conditions.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

from smolagents import MCPClient, OpenAIServerModel, ToolCallingAgent

from config_loader import get_config_loader


class TestBasicServerFunctionality(unittest.TestCase):
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

    def test_sentiment_analysis_neutral(self):
        """Test sentiment analysis with neutral text."""
        if not self.agent:
            self.skipTest("Basic server not available")

        test_cases = [
            "The weather is cloudy today.",
            "This is a standard procedure.",
            "The meeting is scheduled for tomorrow.",
            "The data shows normal patterns.",
            "The system is functioning as expected.",
        ]

        for text in test_cases:
            with self.subTest(text=text[:30] + "..."):
                response = self.agent.run(
                    f"Analyze the sentiment of this text: {text}"
                )
                self.assertIsNotNone(response)
                self.assertIn("sentiment", str(response).lower())

    def test_sentiment_analysis_mixed(self):
        """Test sentiment analysis with mixed sentiment text."""
        if not self.agent:
            self.skipTest("Basic server not available")

        test_cases = [
            "The product is good but expensive.",
            "I like the features but hate the interface.",
            "Great performance but poor documentation.",
            "The service is excellent but the wait time is terrible.",
            "Good quality but bad customer support.",
        ]

        for text in test_cases:
            with self.subTest(text=text[:30] + "..."):
                response = self.agent.run(
                    f"Analyze the sentiment of this text: {text}"
                )
                self.assertIsNotNone(response)
                self.assertIn("sentiment", str(response).lower())

    def test_sentiment_analysis_edge_cases(self):
        """Test sentiment analysis with edge cases."""
        if not self.agent:
            self.skipTest("Basic server not available")

        edge_cases = [
            "",  # Empty string
            "a",  # Single character
            "x" * 1000,  # Very long string
            "!@#$%^&*()",  # Special characters only
            "1234567890",  # Numbers only
            "Hello 世界 🌍",  # Unicode characters
            "   whitespace   ",  # Whitespace
            "\n\t\r",  # Control characters
        ]

        for text in edge_cases:
            with self.subTest(text=repr(text)):
                response = self.agent.run(
                    f"Analyze the sentiment of this text: {text}"
                )
                self.assertIsNotNone(response)


class TestCodeMetricsServerFunctionality(unittest.TestCase):
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

        simple_codes = [
            "def hello(): pass",
            "def add(a, b): return a + b",
            "x = 1",
            "print('Hello')",
        ]

        for code in simple_codes:
            with self.subTest(code=code):
                response = self.agent.run(
                    f"Calculate the complexity of this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("complexity", str(response).lower())

    def test_complexity_analysis_complex(self):
        """Test complexity analysis with complex code."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        complex_codes = [
            """
def fibonacci(n):
    if n <= 1:
        return n
    if n == 2:
        return 1
    if n % 2 == 0:
        return fibonacci(n-1) + fibonacci(n-2)
    else:
        return fibonacci(n-1) + fibonacci(n-2) + 1
""",
            """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item * 3)
        else:
            result.append(0)
    return result
""",
        ]

        for code in complex_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Calculate the complexity of this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("complexity", str(response).lower())

    def test_style_analysis(self):
        """Test code style analysis."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        style_test_codes = [
            """
def bad_style_function( x,y ):
    z=x+y
    return z
""",
            """
def good_style_function(x, y):
    result = x + y
    return result
""",
        ]

        for code in style_test_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze the style of this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("style", str(response).lower())

    def test_naming_conventions(self):
        """Test naming conventions analysis."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        naming_test_codes = [
            """
def BadFunctionName():
    variable_name = "good"
    BAD_CONSTANT = "bad"
    return variable_name
""",
            """
def good_function_name():
    good_variable = "good"
    GOOD_CONSTANT = "good"
    return good_variable
""",
        ]

        for code in naming_test_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze the naming conventions in this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("naming", str(response).lower())

    def test_error_handling_analysis(self):
        """Test error handling analysis."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        error_handling_codes = [
            """
def bad_error_handling():
    x = 1 / 0
    return x
""",
            """
def good_error_handling():
    try:
        x = 1 / 0
        return x
    except ZeroDivisionError:
        return None
""",
        ]

        for code in error_handling_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze the error handling in this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("error", str(response).lower())

    def test_code_coverage_metrics(self):
        """Test code coverage metrics analysis."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        coverage_test_codes = [
            """
def function_with_branches(x):
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"
""",
            """
def function_with_loops():
    result = []
    for i in range(10):
        if i % 2 == 0:
            result.append(i)
    return result
""",
        ]

        for code in coverage_test_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Measure the code coverage metrics of this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("coverage", str(response).lower())

    def test_maintainability_index(self):
        """Test maintainability index calculation."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        maintainability_test_codes = [
            """
def simple_function():
    return "Hello, World!"
""",
            """
def complex_function_with_many_parameters(a, b, c, d, e, f, g, h, i, j):
    result = 0
    if a > 0:
        result += a
    if b > 0:
        result += b
    if c > 0:
        result += c
    if d > 0:
        result += d
    if e > 0:
        result += e
    if f > 0:
        result += f
    if g > 0:
        result += g
    if h > 0:
        result += h
    if i > 0:
        result += i
    if j > 0:
        result += j
    return result
""",
        ]

        for code in maintainability_test_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Calculate the maintainability index of this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("maintainability", str(response).lower())

    def test_performance_metrics(self):
        """Test performance metrics analysis."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        performance_test_codes = [
            """
def efficient_function():
    return [i for i in range(100) if i % 2 == 0]
""",
            """
def inefficient_function():
    result = []
    for i in range(100):
        if i % 2 == 0:
            result.append(i)
    return result
""",
        ]

        for code in performance_test_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Calculate the performance metrics of this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("performance", str(response).lower())

    def test_documentation_quality(self):
        """Test documentation quality analysis."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        documentation_test_codes = [
            """
def undocumented_function(x):
    return x * 2
""",
            """
def well_documented_function(x):
    \"\"\"
    Multiply the input by 2.

    Args:
        x: The number to multiply

    Returns:
        The input multiplied by 2
    \"\"\"
    return x * 2
""",
        ]

        for code in documentation_test_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze the documentation quality of this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("documentation", str(response).lower())

    def test_code_duplication(self):
        """Test code duplication analysis."""
        if not self.agent:
            self.skipTest("Code metrics server not available")

        duplication_test_codes = [
            """
def function1():
    x = 1
    y = 2
    z = x + y
    return z

def function2():
    a = 1
    b = 2
    c = a + b
    return c
""",
            """
def unique_function1():
    return "Hello"

def unique_function2():
    return "World"
""",
        ]

        for code in duplication_test_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Calculate the code duplication in this code: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("duplication", str(response).lower())


class TestCodeSecurityServerFunctionality(unittest.TestCase):
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

    def test_command_injection_detection(self):
        """Test command injection vulnerability detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        vulnerable_codes = [
            """
import os
def dangerous_function(user_input):
    os.system(user_input)
""",
            """
import subprocess
def dangerous_function(user_input):
    subprocess.call(user_input, shell=True)
""",
        ]

        for code in vulnerable_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this code for command injection vulnerabilities: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("injection", str(response).lower())

    def test_sql_injection_detection(self):
        """Test SQL injection vulnerability detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        vulnerable_codes = [
            """
import sqlite3
def vulnerable_query(user_input):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor.execute(query)
    return cursor.fetchall()
""",
            """
import mysql.connector
def vulnerable_query(user_input):
    conn = mysql.connector.connect(host="localhost", user="user", password="pass", database="db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    cursor.execute(query)
    return cursor.fetchall()
""",
        ]

        for code in vulnerable_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this code for SQL injection vulnerabilities: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("sql", str(response).lower())

    def test_code_injection_detection(self):
        """Test code injection vulnerability detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        vulnerable_codes = [
            """
def dangerous_function(user_input):
    eval(user_input)
""",
            """
def dangerous_function(user_input):
    exec(user_input)
""",
            """
def dangerous_function(user_input):
    exec(compile(user_input, '<string>', 'exec'))
""",
        ]

        for code in vulnerable_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this code for code injection vulnerabilities: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("injection", str(response).lower())

    def test_safe_code_analysis(self):
        """Test analysis of safe code."""
        if not self.agent:
            self.skipTest("Code security server not available")

        safe_codes = [
            """
def safe_function(user_input):
    # Sanitize input
    sanitized = user_input.strip()
    return f"Hello, {sanitized}!"
""",
            """
import sqlite3
def safe_query(user_input):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE name = ?"
    cursor.execute(query, (user_input,))
    return cursor.fetchall()
""",
        ]

        for code in safe_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this code for security vulnerabilities: {code}"
                )
                self.assertIsNotNone(response)

    def test_hardcoded_secrets_detection(self):
        """Test hardcoded secrets detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        secrets_test_codes = [
            """
def function_with_secrets():
    password = "secret123"
    api_key = "sk-1234567890abcdef"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    return password
""",
            """
def function_without_secrets():
    password = os.getenv("PASSWORD")
    api_key = os.getenv("API_KEY")
    return password
""",
        ]

        for code in secrets_test_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this code for hardcoded secrets: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("secrets", str(response).lower())

    def test_path_traversal_detection(self):
        """Test path traversal vulnerability detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        path_traversal_codes = [
            """
def vulnerable_function(user_input):
    with open(user_input, 'r') as f:
        return f.read()
""",
            """
def safe_function(user_input):
    import os
    safe_path = os.path.abspath(user_input)
    if safe_path.startswith('/allowed/directory'):
        with open(safe_path, 'r') as f:
            return f.read()
""",
        ]

        for code in path_traversal_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this code for path traversal vulnerabilities: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("traversal", str(response).lower())

    def test_unsafe_deserialization_detection(self):
        """Test unsafe deserialization detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        deserialization_codes = [
            """
import pickle
def dangerous_function(user_input):
    data = pickle.loads(user_input)
    return data
""",
            """
import yaml
def safe_function(user_input):
    data = yaml.safe_load(user_input)
    return data
""",
        ]

        for code in deserialization_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this code for unsafe deserialization: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("deserialization", str(response).lower())

    def test_xss_vulnerability_detection(self):
        """Test XSS vulnerability detection."""
        if not self.agent:
            self.skipTest("Code security server not available")

        xss_codes = [
            """
def vulnerable_function(user_input):
    html = f"<div>{user_input}</div>"
    return html
""",
            """
import html
def safe_function(user_input):
    escaped_input = html.escape(user_input)
    html_content = f"<div>{escaped_input}</div>"
    return html_content
""",
        ]

        for code in xss_codes:
            with self.subTest(code=code[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this code for XSS vulnerabilities: {code}"
                )
                self.assertIsNotNone(response)
                self.assertIn("xss", str(response).lower())


class TestCodeRetrievalServerFunctionality(unittest.TestCase):
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
            "https://httpbin.org/status/200",
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                response = self.agent.run(f"Validate this URL: {url}")
                self.assertIsNotNone(response)
                self.assertIn("valid", str(response).lower())

    def test_url_validation_invalid(self):
        """Test URL validation with invalid URLs."""
        if not self.agent:
            self.skipTest("Code retrieval server not available")

        invalid_urls = [
            "not-a-valid-url",
            "ftp://invalid-protocol.com",
            "http://",
            "https://",
            "invalid://url.com",
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                response = self.agent.run(f"Validate this URL: {url}")
                self.assertIsNotNone(response)

    def test_content_retrieval(self):
        """Test content retrieval from URLs."""
        if not self.agent:
            self.skipTest("Code retrieval server not available")

        test_urls = [
            "https://httpbin.org/json",
            "https://httpbin.org/headers",
            "https://httpbin.org/user-agent",
        ]

        for url in test_urls:
            with self.subTest(url=url):
                response = self.agent.run(f"Retrieve content from: {url}")
                self.assertIsNotNone(response)

    def test_file_content_analysis(self):
        """Test file content analysis."""
        if not self.agent:
            self.skipTest("Code retrieval server not available")

        test_contents = [
            """
def hello_world():
    print("Hello, World!")
    return "Hello, World!"
""",
            """
# This is a Python file
import os
import sys

def main():
    print("Main function")
    return 0

if __name__ == "__main__":
    main()
""",
        ]

        for content in test_contents:
            with self.subTest(content=content[:50] + "..."):
                response = self.agent.run(
                    f"Analyze this file content: {content}"
                )
                self.assertIsNotNone(response)
                self.assertIn("analysis", str(response).lower())

    def test_content_search(self):
        """Test content search functionality."""
        if not self.agent:
            self.skipTest("Code retrieval server not available")

        test_cases = [
            {
                "content": """
def function1():
    print("Hello")

def function2():
    print("World")
""",
                "search_term": "def",
            },
            {
                "content": """
import os
import sys
import json

def main():
    pass
""",
                "search_term": "import",
            },
        ]

        for test_case in test_cases:
            with self.subTest(search_term=test_case["search_term"]):
                response = self.agent.run(
                    f"Search for '{test_case['search_term']}' in this content: {test_case['content']}"
                )
                self.assertIsNotNone(response)
                self.assertIn("search", str(response).lower())

    def test_batch_file_retrieval(self):
        """Test batch file retrieval."""
        if not self.agent:
            self.skipTest("Code retrieval server not available")

        test_urls = [
            "https://httpbin.org/json",
            "https://httpbin.org/headers",
            "https://httpbin.org/user-agent",
        ]

        urls_text = "\n".join(test_urls)
        response = self.agent.run(
            f"Retrieve these files in batch: {urls_text}"
        )
        self.assertIsNotNone(response)
        self.assertIn("batch", str(response).lower())


class TestGitServerFunctionality(unittest.TestCase):
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

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize git repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'Test User'")
            os.system(
                f"cd {temp_path} && git config user.email 'test@example.com'"
            )

            # Create test file
            test_file = temp_path / "test.py"
            test_file.write_text('print("Hello, World!")')

            # Add and commit
            os.system(f"cd {temp_path} && git add .")
            os.system(f"cd {temp_path} && git commit -m 'Initial commit'")

            # Test git status
            response = self.agent.run(
                f"Get the git status of this repository: {temp_path}"
            )
            self.assertIsNotNone(response)
            self.assertIn("status", str(response).lower())

    def test_git_log(self):
        """Test git log functionality."""
        if not self.agent:
            self.skipTest("Git server not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize git repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'Test User'")
            os.system(
                f"cd {temp_path} && git config user.email 'test@example.com'"
            )

            # Create and commit multiple files
            for i in range(3):
                test_file = temp_path / f"file{i}.py"
                test_file.write_text(f'print("File {i}")')
                os.system(f"cd {temp_path} && git add .")
                os.system(f"cd {temp_path} && git commit -m 'Commit {i}'")

            # Test git log
            response = self.agent.run(
                f"Get the git log of this repository: {temp_path}"
            )
            self.assertIsNotNone(response)
            self.assertIn("log", str(response).lower())

    def test_git_branches(self):
        """Test git branch functionality."""
        if not self.agent:
            self.skipTest("Git server not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize git repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'Test User'")
            os.system(
                f"cd {temp_path} && git config user.email 'test@example.com'"
            )

            # Create initial commit
            test_file = temp_path / "main.py"
            test_file.write_text('print("Main branch")')
            os.system(f"cd {temp_path} && git add .")
            os.system(f"cd {temp_path} && git commit -m 'Initial commit'")

            # Create feature branch
            os.system(f"cd {temp_path} && git checkout -b feature-branch")

            # Test branch listing
            response = self.agent.run(
                f"List all branches in this repository: {temp_path}"
            )
            self.assertIsNotNone(response)
            self.assertIn("branch", str(response).lower())

    def test_git_add(self):
        """Test git add functionality."""
        if not self.agent:
            self.skipTest("Git server not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize git repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'Test User'")
            os.system(
                f"cd {temp_path} && git config user.email 'test@example.com'"
            )

            # Create test file
            test_file = temp_path / "new_file.py"
            test_file.write_text('print("New file")')

            # Test git add
            response = self.agent.run(f"Add this file to git: {test_file}")
            self.assertIsNotNone(response)
            self.assertIn("add", str(response).lower())

    def test_git_commit(self):
        """Test git commit functionality."""
        if not self.agent:
            self.skipTest("Git server not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize git repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'Test User'")
            os.system(
                f"cd {temp_path} && git config user.email 'test@example.com'"
            )

            # Create and add test file
            test_file = temp_path / "test.py"
            test_file.write_text('print("Test file")')
            os.system(f"cd {temp_path} && git add .")

            # Test git commit
            response = self.agent.run(
                f"Commit this file with message 'Test commit': {test_file}"
            )
            self.assertIsNotNone(response)
            self.assertIn("commit", str(response).lower())

    def test_git_diff(self):
        """Test git diff functionality."""
        if not self.agent:
            self.skipTest("Git server not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Initialize git repository
            os.system(f"cd {temp_path} && git init")
            os.system(f"cd {temp_path} && git config user.name 'Test User'")
            os.system(
                f"cd {temp_path} && git config user.email 'test@example.com'"
            )

            # Create initial file
            test_file = temp_path / "test.py"
            test_file.write_text('print("Original content")')
            os.system(f"cd {temp_path} && git add .")
            os.system(f"cd {temp_path} && git commit -m 'Initial commit'")

            # Modify file
            test_file.write_text('print("Modified content")')

            # Test git diff
            response = self.agent.run(
                f"Get the git diff for this file: {test_file}"
            )
            self.assertIsNotNone(response)
            self.assertIn("diff", str(response).lower())


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestBasicServerFunctionality,
        TestCodeMetricsServerFunctionality,
        TestCodeSecurityServerFunctionality,
        TestCodeRetrievalServerFunctionality,
        TestGitServerFunctionality,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
