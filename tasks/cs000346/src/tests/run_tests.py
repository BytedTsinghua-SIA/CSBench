#!/usr/bin/env python3
"""
Test runner for TinyChatEngine unit tests
Runs all unit tests independently without dependencies
"""

import unittest
import sys
import os
from pathlib import Path

def run_specific_test(test_module, test_class=None, test_method=None):
    """Run a specific test or test class"""
    # Import the test module
    module_name = f"tests.{test_module}"
    __import__(module_name)
    module = sys.modules[module_name]

    # Create test suite
    loader = unittest.TestLoader()

    if test_method and test_class:
        # Run specific test method
        suite = loader.loadTestsFromName(f"{test_class}.{test_method}", module)
    elif test_class:
        # Run specific test class
        suite = loader.loadTestsFromTestCase(getattr(module, test_class))
    else:
        # Run entire module
        suite = loader.loadTestsFromModule(module)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

def run_all_tests():
    """Run all unit tests"""
    # Discover and run all tests in tests directory
    test_dir = Path(__file__).parent
    src_dir = test_dir.parent

    # Add src directory to Python path for imports
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(test_dir), pattern='test_*.py')

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

def list_available_tests():
    """List all available test modules and classes"""
    test_dir = Path(__file__).parent

    print("Available test modules:")
    for test_file in test_dir.glob('test_*.py'):
        module_name = test_file.stem
        print(f"  {module_name}")

        # Import module to list test classes
        try:
            module_path = f"tests.{module_name}"
            __import__(module_path)
            module = sys.modules[module_path]

            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj != unittest.TestCase:
                    print(f"    {name}")
                    # List test methods
                    for method_name in dir(obj):
                        if method_name.startswith('test_'):
                            print(f"      {method_name}")
        except Exception as e:
            print(f"    Error loading module: {e}")

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run TinyChatEngine unit tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_tests.py

  # Run specific test module
  python run_tests.py -m test_linear_kernel

  # Run specific test class
  python run_tests.py -m test_evaluation -c TestEvaluation

  # Run specific test method
  python run_tests.py -m test_model_downloader -c TestModelDownloader -t test_script_exists

  # List available tests
  python run_tests.py --list
        """
    )

    parser.add_argument('-m', '--module',
                       help='Test module name (without .py extension)')
    parser.add_argument('-c', '--class_name',
                       help='Test class name')
    parser.add_argument('-t', '--method',
                       help='Test method name')
    parser.add_argument('-l', '--list', action='store_true',
                       help='List all available tests')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Set verbosity
    if args.verbose:
        # This will be handled by unittest runner
        pass

    # Add src directory to Python path
    test_dir = Path(__file__).parent
    src_dir = test_dir.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    if args.list:
        list_available_tests()
        return

    try:
        if args.module:
            success = run_specific_test(args.module, args.class_name, args.method)
        else:
            print("Running all unit tests...")
            success = run_all_tests()

        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
