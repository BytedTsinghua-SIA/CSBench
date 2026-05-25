#!/usr/bin/env python
"""
Script to run all unit tests
"""
import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    sys.exit(0 if result.wasSuccessful() else 1)

