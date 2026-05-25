#!/usr/bin/env python3
"""
Prefetcher unit test runner
This script runs all Python unit tests, which test prefetcher core functionality
based on requirements from xxx.txt
"""

import unittest
import sys
import os

def run_all_tests():
    """Discover and run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, test_dir)
    
    test_files = [
        'test_ghb',
        'test_fdp',
        'test_task3'
    ]
    
    print("=" * 60)
    print("Prefetcher Unit Tests")
    print("=" * 60)
    print("Testing C++ prefetcher implementation core functionality")
    print("=" * 60 + "\n")
    
    for test_file in test_files:
        try:
            module = __import__(test_file)
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
        except ImportError as e:
            print(f"Warning: Could not import {test_file}: {e}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    if result.testsRun > 0:
        success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
        print(f"Success rate: {success_rate:.1f}%")
    print("=" * 60)
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

