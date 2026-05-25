#!/usr/bin/env python3
"""
Test runner for network path analyzer unit tests.

This script runs all unit tests for the network path analyzer components.
"""

import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def run_all_tests():
    """Run all unit tests."""
    print("Running Network Path Analyzer Unit Tests")
    print("=" * 50)

    # Check dependencies
    dependencies = ['pandas', 'numpy', 'matplotlib']
    available_deps = []

    for dep in dependencies:
        try:
            __import__(dep)
            available_deps.append(dep)
            print(f"✓ {dep} available")
        except ImportError:
            print(f"⚠ {dep} not available - some tests will be skipped")

    if not available_deps:
        print("\nNo dependencies available. Running minimal tests only...")
        # Only run import tests when no dependencies are available
        suite = unittest.TestSuite()
        suite.addTest(unittest.TestLoader().loadTestsFromName('tests.test_import_only'))
    else:
        print(f"\nAvailable dependencies: {', '.join(available_deps)}")
        # Discover and run all tests
        loader = unittest.TestLoader()
        start_dir = os.path.dirname(__file__)
        suite = loader.discover(start_dir, pattern='test_*.py')

    print(f"\nRunning {suite.countTestCases()} tests")

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print(f"\nResults: {result.testsRun} tests run")
    print(f"  - Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  - Failed: {len(result.failures)}")
    print(f"  - Errors: {len(result.errors)}")
    if hasattr(result, 'skipped'):
        print(f"  - Skipped: {len(result.skipped)}")

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
