#!/usr/bin/env python3
"""
Unified Test Runner for MCP Servers

This script provides a unified interface for running both offline and online tests.
It integrates with the separate offline and online test runners for better organization.
"""

import argparse
import os
import sys
import time

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the separate test runners
try:
    from run_offline_tests import OfflineTestRunner
    from run_online_tests import OnlineTestRunner
    from test_config import (
        create_test_scenario,
        get_available_scenarios,
        validate_test_environment,
    )
except ImportError:
    # If relative imports fail, try absolute imports
    from tests.run_offline_tests import OfflineTestRunner
    from tests.run_online_tests import OnlineTestRunner
    from tests.test_config import (
        create_test_scenario,
        get_available_scenarios,
        validate_test_environment,
    )


class UnifiedTestRunner:
    """Manages both offline and online test execution."""

    def __init__(self):
        self.offline_runner = OfflineTestRunner()
        self.online_runner = OnlineTestRunner()

        # Define test suites
        self.test_suites = {
            "offline": {
                "name": "Offline Tests",
                "description": "Tests that don't require live servers",
                "runner": self.offline_runner,
                "categories": list(self.offline_runner.test_categories.keys()),
            },
            "online": {
                "name": "Online Tests",
                "description": "Tests that require live MCP servers",
                "runner": self.online_runner,
                "categories": list(self.online_runner.test_categories.keys()),
            },
            "all": {
                "name": "All Tests",
                "description": "Both offline and online tests",
                "runner": None,
                "categories": ["offline", "online"],
            },
            "quick": {
                "name": "Quick Tests",
                "description": "Fast offline tests for CI/CD",
                "runner": self.offline_runner,
                "categories": ["configuration", "environment"],
            },
            "health": {
                "name": "Health Tests",
                "description": "Server health and connectivity tests",
                "runner": self.online_runner,
                "categories": ["health"],
            },
            "functionality": {
                "name": "Functionality Tests",
                "description": "All server functionality tests",
                "runner": self.online_runner,
                "categories": [
                    "basic_functionality",
                    "code_metrics_functionality",
                    "code_security_functionality",
                    "code_retrieval_functionality",
                    "git_functionality",
                ],
            },
            "integration": {
                "name": "Integration Tests",
                "description": "Core integration and scenario tests",
                "runner": self.online_runner,
                "categories": ["integration", "scenarios"],
            },
        }

    def list_suites(self):
        """List available test suites."""
        print("Available Test Suites:")
        print("=" * 50)
        for key, info in self.test_suites.items():
            print(f"{key:15} - {info['name']}")
            print(f"{'':15}   {info['description']}")
            if info["categories"]:
                print(f"{'':15}   Categories: {', '.join(info['categories'])}")
            print()

    def list_categories(self):
        """List all available test categories."""
        print("Available Test Categories:")
        print("=" * 50)

        print("📁 OFFLINE CATEGORIES (Safe for CI/CD):")
        print("-" * 30)
        for key, info in self.offline_runner.test_categories.items():
            print(f"{key:25} - {info['name']}")
            print(f"{'':25}   {info['description']}")
        print()

        print("🌐 ONLINE CATEGORIES (Require live servers):")
        print("-" * 30)
        for key, info in self.online_runner.test_categories.items():
            print(f"{key:25} - {info['name']}")
            print(f"{'':25}   {info['description']}")
        print()

    def list_scenarios(self):
        """List available test scenarios."""
        print("Available Test Scenarios:")
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

    def run_suite(self, suite_name: str, verbose: bool = False) -> dict:
        """Run a specific test suite."""
        if suite_name not in self.test_suites:
            return {
                "success": False,
                "error": f"Unknown suite: {suite_name}",
                "tests_run": 0,
                "failures": 0,
                "errors": 0,
            }

        suite_info = self.test_suites[suite_name]

        if suite_name == "all":
            # Run both offline and online tests
            return self.run_all_tests(verbose)
        elif suite_name == "quick":
            # Run quick offline tests
            return self.offline_runner.run_all_offline_tests(verbose)
        elif suite_name == "health":
            # Run health tests
            return self.online_runner.run_health_tests(verbose)
        elif suite_name == "functionality":
            # Run functionality tests
            return self.online_runner.run_functionality_tests(verbose)
        elif suite_name == "integration":
            # Run integration tests
            return self.run_integration_tests(verbose)
        elif suite_name == "offline":
            # Run all offline tests
            return self.offline_runner.run_all_offline_tests(verbose)
        elif suite_name == "online":
            # Run all online tests
            return self.online_runner.run_all_online_tests(verbose)
        else:
            # Run specific categories
            return self.run_categories(suite_info["categories"], verbose)

    def run_categories(self, categories: list, verbose: bool = False) -> dict:
        """Run tests for specific categories."""
        results = {}
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0

        for category in categories:
            # Determine which runner to use
            if category in self.offline_runner.test_categories:
                result = self.offline_runner.run_category(category, verbose)
            elif category in self.online_runner.test_categories:
                result = self.online_runner.run_category(category, verbose)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown category: {category}",
                    "tests_run": 0,
                    "failures": 0,
                    "errors": 0,
                }

            results[category] = result
            total_tests += result["tests_run"]
            total_failures += result["failures"]
            total_errors += result["errors"]
            total_skipped += result.get("skipped", 0)

        overall_success = all(result["success"] for result in results.values())

        return {
            "success": overall_success,
            "categories": results,
            "total_tests": total_tests,
            "total_failures": total_failures,
            "total_errors": total_errors,
            "total_skipped": total_skipped,
        }

    def run_all_tests(self, verbose: bool = False) -> dict:
        """Run all tests (both offline and online)."""
        print("Running All Tests (Offline + Online)...")
        print("=" * 50)
        print("⚠️  WARNING: Online tests require live MCP servers!")
        print()

        # Run offline tests first
        print("📁 Running Offline Tests...")
        offline_results = self.offline_runner.run_all_offline_tests(verbose)

        print("\n" + "=" * 50)

        # Check if online tests should be run
        if not offline_results["success"]:
            print("❌ Offline tests failed. Skipping online tests.")
            return offline_results

        # Check for API key
        if not os.getenv("TOGETHER_API_KEY"):
            print("❌ TOGETHER_API_KEY not set. Skipping online tests.")
            return offline_results

        # Run online tests
        print("🌐 Running Online Tests...")
        online_results = self.online_runner.run_all_online_tests(verbose)

        # Combine results
        combined_results = {
            "success": offline_results["success"]
            and online_results["success"],
            "offline": offline_results,
            "online": online_results,
            "total_tests": offline_results["total_tests"]
            + online_results["total_tests"],
            "total_failures": offline_results["total_failures"]
            + online_results["total_failures"],
            "total_errors": offline_results["total_errors"]
            + online_results["total_errors"],
            "total_skipped": offline_results["total_skipped"]
            + online_results["total_skipped"],
        }

        return combined_results

    def run_integration_tests(self, verbose: bool = False) -> dict:
        """Run integration tests."""
        print("Running Integration Tests...")
        print("=" * 50)
        print("⚠️  WARNING: These tests require live MCP servers!")

        integration_categories = ["integration", "scenarios"]
        return self.run_categories(integration_categories, verbose)

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

        return self.run_categories(scenario.get_categories(), verbose)

    def generate_report(self, results: dict) -> str:
        """Generate a detailed test report."""
        report = []
        report.append("MCP Server Test Report")
        report.append("=" * 50)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        if "offline" in results and "online" in results:
            # Combined report
            report.append("📁 OFFLINE TESTS")
            report.append("-" * 20)
            offline = results["offline"]
            for category, result in offline["categories"].items():
                report.append(
                    f"   {category}: {'✅ PASSED' if result['success'] else '❌ FAILED'}"
                )
            report.append(
                f"   Total: {offline['total_tests']} tests, {offline['total_failures']} failures"
            )
            report.append("")

            report.append("🌐 ONLINE TESTS")
            report.append("-" * 20)
            online = results["online"]
            for category, result in online["categories"].items():
                report.append(
                    f"   {category}: {'✅ PASSED' if result['success'] else '❌ FAILED'}"
                )
            report.append(
                f"   Total: {online['total_tests']} tests, {online['total_failures']} failures"
            )
            report.append("")

            report.append("📈 OVERALL SUMMARY")
            report.append("-" * 20)
            report.append(f"   Total Tests: {results['total_tests']}")
            report.append(f"   Total Failures: {results['total_failures']}")
            report.append(f"   Total Errors: {results['total_errors']}")
            report.append(f"   Total Skipped: {results['total_skipped']}")
            report.append("")
        elif "categories" in results:
            # Detailed report for multiple categories
            for category, result in results["categories"].items():
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
    """Main function for the unified test runner."""
    parser = argparse.ArgumentParser(description="Run MCP Server Tests")
    parser.add_argument(
        "suite",
        nargs="?",
        choices=[
            "all",
            "offline",
            "online",
            "quick",
            "health",
            "functionality",
            "integration",
            "list",
            "list-categories",
            "list-scenarios",
            "validate",
        ]
        + get_available_scenarios(),
        default="all",
        help="Test suite or scenario to run",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate detailed report"
    )
    parser.add_argument(
        "--offline-only",
        action="store_true",
        help="Run only offline tests (safe for CI)",
    )
    parser.add_argument(
        "--online-only",
        action="store_true",
        help="Run only online tests (requires servers)",
    )

    args = parser.parse_args()

    runner = UnifiedTestRunner()

    if args.suite == "list":
        runner.list_suites()
        return
    elif args.suite == "list-categories":
        runner.list_categories()
        return
    elif args.suite == "list-scenarios":
        runner.list_scenarios()
        return
    elif args.suite == "validate":
        success = runner.validate_environment()
        sys.exit(0 if success else 1)

    # Handle offline/online only flags
    if args.offline_only:
        if args.suite in ["online", "health", "functionality", "integration"]:
            print("❌ Cannot run online tests with --offline-only flag")
            sys.exit(1)
        args.suite = "offline"
    elif args.online_only:
        if args.suite in ["offline", "quick"]:
            print("❌ Cannot run offline tests with --online-only flag")
            sys.exit(1)
        args.suite = "online"

    print("🚀 MCP Server Test Runner")
    print("=" * 50)

    start_time = time.time()

    # Check if it's a scenario
    if args.suite in get_available_scenarios():
        results = runner.run_scenario(args.suite, args.verbose)
    else:
        results = runner.run_suite(args.suite, args.verbose)

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
