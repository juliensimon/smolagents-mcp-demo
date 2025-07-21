#!/usr/bin/env python3
"""
MCP Demo Test Runner

This script provides a convenient way to run tests from the project root.
It delegates to the comprehensive test suite in the tests/ directory.
"""

import os
import sys

from tests.run_tests import main

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    main()
