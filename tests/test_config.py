#!/usr/bin/env python3
"""
Test Configuration and Scenarios

This module defines test configurations and scenarios for different testing purposes.
"""

import os
from typing import Any, Dict, List, Optional


class TestConfig:
    """Configuration for test scenarios."""

    # Test scenarios
    SCENARIOS = {
        "smoke": {
            "name": "Smoke Tests",
            "description": "Basic functionality tests to ensure servers are working",
            "categories": ["environment", "health", "basic_functionality"],
            "timeout": 30,
        },
        "integration": {
            "name": "Integration Tests",
            "description": "Full integration tests with all servers",
            "categories": ["integration", "scenarios"],
            "timeout": 120,
        },
        "functionality": {
            "name": "Functionality Tests",
            "description": "Detailed functionality tests for each server",
            "categories": [
                "basic_functionality",
                "code_metrics_functionality",
                "code_security_functionality",
                "code_retrieval_functionality",
                "git_functionality",
            ],
            "timeout": 180,
        },
        "performance": {
            "name": "Performance Tests",
            "description": "Performance and stress tests",
            "categories": ["integration"],
            "timeout": 300,
            "performance_mode": True,
        },
        "security": {
            "name": "Security Tests",
            "description": "Security-focused tests",
            "categories": ["code_security_functionality"],
            "timeout": 60,
        },
        "full": {
            "name": "Full Test Suite",
            "description": "Complete test suite with all categories",
            "categories": [
                "environment",
                "configuration",
                "health",
                "integration",
                "scenarios",
                "basic_functionality",
                "code_metrics_functionality",
                "code_security_functionality",
                "code_retrieval_functionality",
                "git_functionality",
            ],
            "timeout": 600,
        },
    }

    # Test data
    TEST_DATA = {
        "sentiment": {
            "positive": [
                "I love this product! It's absolutely amazing.",
                "This is the best experience I've ever had.",
                "Fantastic service and wonderful support!",
                "I'm so happy with the results!",
                "Excellent quality and great value for money.",
            ],
            "negative": [
                "I hate this product. It's terrible.",
                "This is the worst experience ever.",
                "Terrible service and poor quality.",
                "I'm very disappointed with the results.",
                "Awful customer support and bad product.",
            ],
            "neutral": [
                "The weather is cloudy today.",
                "This is a standard procedure.",
                "The meeting is scheduled for tomorrow.",
                "The data shows normal patterns.",
                "The system is functioning as expected.",
            ],
            "mixed": [
                "The product is good but expensive.",
                "I like the features but hate the interface.",
                "Great performance but poor documentation.",
                "The service is excellent but the wait time is terrible.",
                "Good quality but bad customer support.",
            ],
        },
        "code": {
            "simple": [
                "def hello(): pass",
                "def add(a, b): return a + b",
                "x = 1",
                "print('Hello')",
            ],
            "complex": [
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
            ],
            "vulnerable": [
                """
import os
def dangerous_function(user_input):
    os.system(user_input)
""",
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
def dangerous_function(user_input):
    eval(user_input)
""",
            ],
            "safe": [
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
            ],
        },
        "urls": {
            "valid": [
                "https://httpbin.org/json",
                "https://api.github.com/users/octocat",
                "https://jsonplaceholder.typicode.com/posts/1",
                "https://httpbin.org/status/200",
            ],
            "invalid": [
                "not-a-valid-url",
                "ftp://invalid-protocol.com",
                "http://",
                "https://",
                "invalid://url.com",
            ],
        },
    }

    # Performance test configurations
    PERFORMANCE_CONFIG = {
        "concurrent_requests": 10,
        "request_delay": 0.1,
        "memory_threshold_mb": 100,
        "response_time_threshold": 30.0,
    }

    # Environment requirements
    ENVIRONMENT_REQUIREMENTS = {
        "python_version": "3.8+",
        "required_env_vars": ["TOGETHER_API_KEY"],
        "required_packages": [
            "smolagents",
            "requests",
            "gradio",
            "textblob",
            "psutil",
        ],
        "server_ports": [7860, 7861, 7862, 7863, 7864],
    }

    @classmethod
    def get_scenario(cls, scenario_name: str) -> Dict[str, Any]:
        """Get a specific test scenario configuration."""
        return cls.SCENARIOS.get(scenario_name, {})

    @classmethod
    def list_scenarios(cls) -> List[str]:
        """List all available test scenarios."""
        return list(cls.SCENARIOS.keys())

    @classmethod
    def get_test_data(cls, category: str, subcategory: Optional[str] = None) -> Any:
        """Get test data for a specific category."""
        if subcategory:
            return cls.TEST_DATA.get(category, {}).get(subcategory, [])
        return cls.TEST_DATA.get(category, {})

    @classmethod
    def validate_environment(cls) -> Dict[str, bool]:
        """Validate that the environment meets requirements."""
        import sys

        validation_results = {}

        # Check Python version
        version = sys.version_info
        validation_results["python_version"] = version.major == 3 and version.minor >= 8

        # Check environment variables
        required_env_vars: List[str] = cls.ENVIRONMENT_REQUIREMENTS["required_env_vars"]  # type: ignore
        validation_results["env_vars"] = all(
            os.getenv(var) for var in required_env_vars
        )

        # Check required packages
        required_packages: List[str] = cls.ENVIRONMENT_REQUIREMENTS["required_packages"]  # type: ignore
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        validation_results["packages"] = len(missing_packages) == 0
        validation_results["missing_packages"] = missing_packages  # type: ignore

        return validation_results

    @classmethod
    def get_performance_config(cls) -> Dict[str, Any]:
        """Get performance test configuration."""
        return cls.PERFORMANCE_CONFIG.copy()

    @classmethod
    def get_environment_requirements(cls) -> Dict[str, Any]:
        """Get environment requirements."""
        return cls.ENVIRONMENT_REQUIREMENTS.copy()


class TestScenario:
    """Represents a test scenario with its configuration."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.categories = config.get("categories", [])
        self.timeout = config.get("timeout", 60)
        self.performance_mode = config.get("performance_mode", False)

    def get_description(self) -> str:
        """Get scenario description."""
        return self.config.get("description", "")

    def should_run_performance_tests(self) -> bool:
        """Check if performance tests should be run."""
        return self.performance_mode

    def get_timeout(self) -> int:
        """Get scenario timeout in seconds."""
        return self.timeout

    def get_categories(self) -> List[str]:
        """Get test categories for this scenario."""
        return self.categories.copy()


def create_test_scenario(scenario_name: str) -> TestScenario:
    """Create a test scenario from configuration."""
    config = TestConfig.get_scenario(scenario_name)
    if not config:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    return TestScenario(scenario_name, config)


def get_available_scenarios() -> List[str]:
    """Get list of available test scenarios."""
    return TestConfig.list_scenarios()


def validate_test_environment() -> Dict[str, bool]:
    """Validate the test environment."""
    return TestConfig.validate_environment()


if __name__ == "__main__":
    # Print available scenarios
    print("Available Test Scenarios:")
    print("=" * 50)

    for scenario_name in get_available_scenarios():
        scenario = create_test_scenario(scenario_name)
        print(f"{scenario_name:15} - {scenario.get_description()}")
        print(f"{'':15}   Categories: {', '.join(scenario.get_categories())}")
        print(f"{'':15}   Timeout: {scenario.get_timeout()}s")
        print()

    # Validate environment
    print("Environment Validation:")
    print("=" * 50)

    validation = validate_test_environment()
    for check, result in validation.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check:20} - {status}")

    missing_packages: List[str] = validation.get("missing_packages", [])  # type: ignore
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
