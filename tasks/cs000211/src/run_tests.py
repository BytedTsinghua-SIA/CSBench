#!/usr/bin/env python
"""
Run all unit tests
"""
import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

def run_all_tests():
    """Run all tests"""
    # Discover and load all tests
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=os.path.join(os.path.dirname(__file__), 'tests'),
        pattern='test_*.py'
    )
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return test results
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

