#!/usr/bin/env python3
"""
Online Test Runner

This script runs tests that require live MCP servers and endpoints.
These tests should NOT be run in CI environments where servers are not available.
"""

import argparse
import os
import sys
import time
import unittest

# Add the parent directory to the path so we can import from tests
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from tests.test_online import (
    TestBasicServerFunctionalityOnline,
    TestCodeMetricsServerFunctionalityOnline,
    TestCodeRetrievalServerFunctionalityOnline,
    TestCodeSecurityServerFunctionalityOnline,
    TestGitServerFunctionalityOnline,
    TestIntegrationScenariosOnline,
    TestMCPIntegrationOnline,
    TestServerHealthOnline,
)


class OnlineTestRunner:
    """Manages online test execution and reporting."""

    def __init__(self):
        self.test_categories = {
            "integration": {
                "name": "MCP Integration Tests",
                "class": TestMCPIntegrationOnline,
                "description": "Real MCP server integration tests",
            },
            "health": {
                "name": "Server Health Tests",
                "class": TestServerHealthOnline,
                "description": "Server health and connectivity tests",
            },
            "basic_functionality": {
                "name": "Basic Server Functionality",
                "class": TestBasicServerFunctionalityOnline,
                "description": "Detailed basic server functionality tests",
            },
            "code_metrics_functionality": {
                "name": "Code Metrics Functionality",
                "class": TestCodeMetricsServerFunctionalityOnline,
                "description": "Detailed code metrics server functionality tests",
            },
            "code_security_functionality": {
                "name": "Code Security Functionality",
                "class": TestCodeSecurityServerFunctionalityOnline,
                "description": "Detailed code security server functionality tests",
            },
            "code_retrieval_functionality": {
                "name": "Code Retrieval Functionality",
                "class": TestCodeRetrievalServerFunctionalityOnline,
                "description": "Detailed code retrieval server functionality tests",
            },
            "git_functionality": {
                "name": "Git Server Functionality",
                "class": TestGitServerFunctionalityOnline,
                "description": "Detailed git server functionality tests",
            },
            "scenarios": {
                "name": "Integration Scenarios",
                "class": TestIntegrationScenariosOnline,
                "description": "Complex integration scenarios and workflows",
            },
        }

    def list_categories(self):
        """List available online test categories."""
        print("Available online test categories:")
        print("=" * 50)
        for key, info in self.test_categories.items():
            print(f"{key:25} - {info['name']}")
            print(f"{'':25}   {info['description']}")
            print()

    def run_category(self, category: str, verbose: bool = False) -> dict:
        """Run tests for a specific category."""
        if category not in self.test_categories:
            return {
                "success": False,
                "error": f"Unknown category: {category}",
                "tests_run": 0,
                "failures": 0,
                "errors": 0,
            }

        category_info = self.test_categories[category]
        test_class = category_info["class"]

        # Create test suite
        test_suite = unittest.TestSuite()
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

        # Run tests
        verbosity = 2 if verbose else 1
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(test_suite)

        return {
            "success": result.wasSuccessful(),
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, "skipped") else 0,
        }

    def run_all_online_tests(self, verbose: bool = False) -> dict:
        """Run all online test categories."""
        print("Running All Online Test Categories...")
        print("=" * 50)
        print("⚠️  WARNING: These tests require live MCP servers and endpoints!")
        print("   Make sure all servers are running before proceeding.")
        print()

        results = {}
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0

        for category in self.test_categories:
            print(f"\n{'=' * 20} {category.upper()} {'=' * 20}")
            result = self.run_category(category, verbose)
            results[category] = result

            total_tests += result["tests_run"]
            total_failures += result["failures"]
            total_errors += result["errors"]
            total_skipped += result.get("skipped", 0)

            if not result["success"]:
                print(f"❌ {category}: {result.get('error', 'Unknown error')}")

        overall_success = all(result["success"] for result in results.values())

        return {
            "success": overall_success,
            "categories": results,
            "total_tests": total_tests,
            "total_failures": total_failures,
            "total_errors": total_errors,
            "total_skipped": total_skipped,
        }

    def run_health_tests(self, verbose: bool = False) -> dict:
        """Run health tests to check server connectivity."""
        print("Running Health Tests...")
        print("=" * 50)
        print("⚠️  WARNING: These tests require live MCP servers!")

        return self.run_category("health", verbose)

    def run_functionality_tests(self, verbose: bool = False) -> dict:
        """Run all server functionality tests."""
        print("Running Server Functionality Tests...")
        print("=" * 50)
        print("⚠️  WARNING: These tests require live MCP servers and endpoints!")

        functionality_categories = [
            "basic_functionality",
            "code_metrics_functionality",
            "code_security_functionality",
            "code_retrieval_functionality",
            "git_functionality",
        ]
        results = {}

        for category in functionality_categories:
            print(f"\nTesting {category}...")
            result = self.run_category(category, verbose)
            results[category] = result

        overall_success = all(result["success"] for result in results.values())

        return {"success": overall_success, "categories": results}

    def generate_report(self, results: dict) -> str:
        """Generate a detailed test report."""
        report = []
        report.append("Online Test Report")
        report.append("=" * 50)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        if "categories" in results:
            # Detailed report for multiple categories
            for category, result in results["categories"].items():
                if category in self.test_categories:
                    category_info = self.test_categories[category]
                    report.append(f"📊 {category_info['name']}")
                else:
                    report.append(f"📊 {category}")
                report.append(f"   Tests Run: {result['tests_run']}")
                report.append(f"   Failures: {result['failures']}")
                report.append(f"   Errors: {result['errors']}")
                report.append(f"   Skipped: {result.get('skipped', 0)}")
                report.append(
                    f"   Status: {'✅ PASSED' if result['success'] else '❌ FAILED'}"
                )
                report.append("")

            if "total_tests" in results:
                report.append("📈 Summary")
                report.append(f"   Total Tests: {results['total_tests']}")
                report.append(f"   Total Failures: {results['total_failures']}")
                report.append(f"   Total Errors: {results['total_errors']}")
                report.append(f"   Total Skipped: {results['total_skipped']}")
                report.append("")
        else:
            # Single category report
            result = results
            report.append("📊 Test Results")
            report.append(f"   Tests Run: {result['tests_run']}")
            report.append(f"   Failures: {result['failures']}")
            report.append(f"   Errors: {result['errors']}")
            report.append(f"   Skipped: {result.get('skipped', 0)}")
            report.append("")

        report.append(
            f"Overall Status: {'🎉 ALL TESTS PASSED' if results['success'] else '❌ SOME TESTS FAILED'}"
        )

        return "\n".join(report)


def main():
    """Main function for the online test runner."""
    parser = argparse.ArgumentParser(description="Run Online MCP Tests")
    parser.add_argument(
        "category",
        nargs="?",
        choices=[
            "all",
            "health",
            "functionality",
            "integration",
            "scenarios",
            "basic_functionality",
            "code_metrics_functionality",
            "code_security_functionality",
            "code_retrieval_functionality",
            "git_functionality",
            "list",
        ],
        default="all",
        help="Test category to run",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--report", action="store_true", help="Generate detailed report"
    )

    args = parser.parse_args()

    runner = OnlineTestRunner()

    if args.category == "list":
        runner.list_categories()
        return

    print("🚀 MCP Online Test Runner")
    print("=" * 50)
    print("⚠️  WARNING: These tests require live MCP servers and endpoints!")
    print("   Make sure all servers are running before proceeding.")
    print()

    # Check if TOGETHER_API_KEY is set
    if not os.getenv("TOGETHER_API_KEY"):
        print("❌ ERROR: TOGETHER_API_KEY environment variable is not set!")
        print("   Please set it before running online tests.")
        sys.exit(1)

    start_time = time.time()

    if args.category == "all":
        results = runner.run_all_online_tests(args.verbose)
    elif args.category == "health":
        results = runner.run_health_tests(args.verbose)
    elif args.category == "functionality":
        results = runner.run_functionality_tests(args.verbose)
    else:
        results = runner.run_category(args.category, args.verbose)

    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "=" * 50)
    print(f"Test execution completed in {duration:.2f} seconds")

    if args.report:
        report = runner.generate_report(results)
        print("\n" + report)

    if results["success"]:
        print("\n🎉 All online tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some online tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
