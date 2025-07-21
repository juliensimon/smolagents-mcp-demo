#!/usr/bin/env python3
"""
Offline Test Runner

This script runs tests that can execute without live MCP servers or endpoints.
These tests are safe to run in CI environments where servers are not available.
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

from tests.test_offline import (
    TestConfigurationOffline,
    TestConfigValidationOffline,
    TestEnvironmentOffline,
    TestFileStructureOffline,
)


class OfflineTestRunner:
    """Manages offline test execution and reporting."""

    def __init__(self):
        self.test_categories = {
            "configuration": {
                "name": "Configuration Tests",
                "class": TestConfigurationOffline,
                "description": "Configuration structure and validation tests",
            },
            "environment": {
                "name": "Environment Tests",
                "class": TestEnvironmentOffline,
                "description": "Environment setup and dependency tests",
            },
            "config_validation": {
                "name": "Config Validation Tests",
                "class": TestConfigValidationOffline,
                "description": "Configuration file validation tests",
            },
            "file_structure": {
                "name": "File Structure Tests",
                "class": TestFileStructureOffline,
                "description": "File structure and import tests",
            },
        }

    def list_categories(self):
        """List available offline test categories."""
        print("Available offline test categories:")
        print("=" * 50)
        for key, info in self.test_categories.items():
            print(f"{key:20} - {info['name']}")
            print(f"{'':20}   {info['description']}")
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

    def run_all_offline_tests(self, verbose: bool = False) -> dict:
        """Run all offline test categories."""
        print("Running All Offline Test Categories...")
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

    def generate_report(self, results: dict) -> str:
        """Generate a detailed test report."""
        report = []
        report.append("Offline Test Report")
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
    """Main function for the offline test runner."""
    parser = argparse.ArgumentParser(description="Run Offline MCP Tests")
    parser.add_argument(
        "category",
        nargs="?",
        choices=[
            "all",
            "configuration",
            "environment",
            "config_validation",
            "file_structure",
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

    runner = OfflineTestRunner()

    if args.category == "list":
        runner.list_categories()
        return

    print("🚀 MCP Offline Test Runner")
    print("=" * 50)
    print("Running tests that don't require live servers or endpoints...")

    start_time = time.time()

    if args.category == "all":
        results = runner.run_all_offline_tests(args.verbose)
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
        print("\n🎉 All offline tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some offline tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
