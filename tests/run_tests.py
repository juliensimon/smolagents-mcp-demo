#!/usr/bin/env python3
"""
Simplified Test Runner for MCP Servers

This script runs the comprehensive MCP integration test suite.
"""

import argparse
import os
import sys
import time
import unittest

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_config import (
    TestConfig,
    create_test_scenario,
    get_available_scenarios,
    validate_test_environment,
)
from tests.test_mcp_integration import (
    TestConfiguration,
    TestEnvironment,
    TestIntegrationScenarios,
    TestMCPIntegration,
    TestServerHealth,
)
from tests.test_server_functionality import (
    TestBasicServerFunctionality,
    TestCodeMetricsServerFunctionality,
    TestCodeRetrievalServerFunctionality,
    TestCodeSecurityServerFunctionality,
    TestGitServerFunctionality,
)


class TestRunner:
    """Manages test execution and reporting."""

    def __init__(self):
        self.test_categories = {
            "integration": {
                "name": "MCP Integration Tests",
                "class": TestMCPIntegration,
                "description": "Real MCP server integration tests",
            },
            "configuration": {
                "name": "Configuration Tests",
                "class": TestConfiguration,
                "description": "Configuration validation tests",
            },
            "environment": {
                "name": "Environment Tests",
                "class": TestEnvironment,
                "description": "Environment setup tests",
            },
            "health": {
                "name": "Server Health Tests",
                "class": TestServerHealth,
                "description": "Server health and connectivity tests",
            },
            "scenarios": {
                "name": "Integration Scenarios",
                "class": TestIntegrationScenarios,
                "description": "Complex integration scenarios and workflows",
            },
            "basic_functionality": {
                "name": "Basic Server Functionality",
                "class": TestBasicServerFunctionality,
                "description": "Detailed basic server functionality tests",
            },
            "code_metrics_functionality": {
                "name": "Code Metrics Functionality",
                "class": TestCodeMetricsServerFunctionality,
                "description": "Detailed code metrics server functionality tests",
            },
            "code_security_functionality": {
                "name": "Code Security Functionality",
                "class": TestCodeSecurityServerFunctionality,
                "description": "Detailed code security server functionality tests",
            },
            "code_retrieval_functionality": {
                "name": "Code Retrieval Functionality",
                "class": TestCodeRetrievalServerFunctionality,
                "description": "Detailed code retrieval server functionality tests",
            },
            "git_functionality": {
                "name": "Git Server Functionality",
                "class": TestGitServerFunctionality,
                "description": "Detailed git server functionality tests",
            },
        }

    def list_categories(self):
        """List available test categories."""
        print("Available test categories:")
        print("=" * 50)
        for key, info in self.test_categories.items():
            print(f"{key:25} - {info['name']}")
            print(f"{'':25}   {info['description']}")
            print()

    def list_scenarios(self):
        """List available test scenarios."""
        print("Available test scenarios:")
        print("=" * 50)

        for scenario_name in get_available_scenarios():
            try:
                scenario = create_test_scenario(scenario_name)
                print(f"{scenario_name:15} - {scenario.get_description()}")
                print(
                    f"{'':15}   Categories: {', '.join(scenario.get_categories())}"
                )
                print(f"{'':15}   Timeout: {scenario.get_timeout()}s")
                print()
            except Exception as e:
                print(f"{scenario_name:15} - Error: {e}")
                print()

    def validate_environment(self):
        """Validate the test environment."""
        print("Environment Validation:")
        print("=" * 50)

        validation = validate_test_environment()
        all_passed = True

        for check, result in validation.items():
            if check == "missing_packages":
                continue
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{check:20} - {status}")
            if not result:
                all_passed = False

        if validation.get("missing_packages"):
            print(
                f"\nMissing packages: {', '.join(validation['missing_packages'])}"
            )
            all_passed = False

        print(
            f"\nOverall: {'✅ ALL CHECKS PASSED' if all_passed else '❌ SOME CHECKS FAILED'}"
        )
        return all_passed

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
            "skipped": len(result.skipped)
            if hasattr(result, "skipped")
            else 0,
        }

    def run_scenario(self, scenario_name: str, verbose: bool = False) -> dict:
        """Run tests for a specific scenario."""
        try:
            scenario = create_test_scenario(scenario_name)
        except ValueError as e:
            return {
                "success": False,
                "error": str(e),
                "tests_run": 0,
                "failures": 0,
                "errors": 0,
            }

        print(f"Running scenario: {scenario.name}")
        print(f"Description: {scenario.get_description()}")
        print(f"Categories: {', '.join(scenario.get_categories())}")
        print(f"Timeout: {scenario.get_timeout()}s")
        print("=" * 50)

        results = {}
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0

        for category in scenario.get_categories():
            if category in self.test_categories:
                print(f"\nTesting {category}...")
                result = self.run_category(category, verbose)
                results[category] = result

                total_tests += result["tests_run"]
                total_failures += result["failures"]
                total_errors += result["errors"]
                total_skipped += result.get("skipped", 0)
            else:
                print(
                    f"Warning: Unknown category '{category}' in scenario '{scenario_name}'"
                )

        overall_success = all(result["success"] for result in results.values())

        return {
            "success": overall_success,
            "scenario": scenario_name,
            "categories": results,
            "total_tests": total_tests,
            "total_failures": total_failures,
            "total_errors": total_errors,
            "total_skipped": total_skipped,
        }

    def run_all_tests(self, verbose: bool = False) -> dict:
        """Run all test categories."""
        print("Running All Test Categories...")
        print("=" * 50)

        results = {}
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0

        for category in self.test_categories:
            print(f"\n{'=' * 20} {category.upper()} {'=' * 20}")
            result = self.run_category(category, verbose)
            results[category] = result

            if result["success"]:
                total_tests += result["tests_run"]
                total_failures += result["failures"]
                total_errors += result["errors"]
                total_skipped += result.get("skipped", 0)
            else:
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

    def run_quick_tests(self, verbose: bool = False) -> dict:
        """Run quick tests (environment and configuration only)."""
        print("Running Quick Tests (Environment & Configuration)...")
        print("=" * 50)

        quick_categories = ["environment", "configuration"]
        results = {}

        for category in quick_categories:
            print(f"\nTesting {category}...")
            result = self.run_category(category, verbose)
            results[category] = result

        overall_success = all(result["success"] for result in results.values())

        return {"success": overall_success, "categories": results}

    def run_health_tests(self, verbose: bool = False) -> dict:
        """Run health tests to check server connectivity."""
        print("Running Health Tests...")
        print("=" * 50)

        return self.run_category("health", verbose)

    def run_core_tests(self, verbose: bool = False) -> dict:
        """Run core functionality tests (integration and scenarios)."""
        print("Running Core Functionality Tests...")
        print("=" * 50)

        core_categories = ["integration", "scenarios"]
        results = {}

        for category in core_categories:
            print(f"\nTesting {category}...")
            result = self.run_category(category, verbose)
            results[category] = result

        overall_success = all(result["success"] for result in results.values())

        return {"success": overall_success, "categories": results}

    def run_functionality_tests(self, verbose: bool = False) -> dict:
        """Run all server functionality tests."""
        print("Running Server Functionality Tests...")
        print("=" * 50)

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
        report.append("MCP Server Test Report")
        report.append("=" * 50)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        if "scenario" in results:
            # Scenario report
            report.append(f"Scenario: {results['scenario']}")
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
                report.append(
                    f"   Total Failures: {results['total_failures']}"
                )
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
    """Main function for the test runner."""
    parser = argparse.ArgumentParser(description="Run MCP Server Tests")
    parser.add_argument(
        "category",
        nargs="?",
        choices=[
            "all",
            "quick",
            "health",
            "core",
            "functionality",
            "list",
            "list-scenarios",
            "validate",
            "integration",
            "configuration",
            "environment",
            "scenarios",
            "basic_functionality",
            "code_metrics_functionality",
            "code_security_functionality",
            "code_retrieval_functionality",
            "git_functionality",
        ]
        + get_available_scenarios(),
        default="all",
        help="Test category or scenario to run",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate detailed report"
    )

    args = parser.parse_args()

    runner = TestRunner()

    if args.category == "list":
        runner.list_categories()
        return
    elif args.category == "list-scenarios":
        runner.list_scenarios()
        return
    elif args.category == "validate":
        success = runner.validate_environment()
        sys.exit(0 if success else 1)

    print("🚀 MCP Server Test Runner")
    print("=" * 50)

    start_time = time.time()

    # Check if it's a scenario
    if args.category in get_available_scenarios():
        results = runner.run_scenario(args.category, args.verbose)
    elif args.category == "all":
        results = runner.run_all_tests(args.verbose)
    elif args.category == "quick":
        results = runner.run_quick_tests(args.verbose)
    elif args.category == "health":
        results = runner.run_health_tests(args.verbose)
    elif args.category == "core":
        results = runner.run_core_tests(args.verbose)
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
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
