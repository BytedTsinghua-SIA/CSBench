#!/usr/bin/env python3
"""
Test runner for all satellite control system unit tests
"""

import unittest
import sys
import os

# Add the tests directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import all test modules
from test_remus import TestRemusSatelliteControl
from test_spica import TestSpicaNavigationSystem
from test_polaris import TestPolarisCommunicationSystem
from test_vega import TestVegaDataStorage
from test_deneb import TestDenebTelemetrySystem
from test_antares import TestAntaresSynchronization
from test_rigel import TestRigelAdvancedControl


def create_test_suite():
    """Create a test suite containing all satellite system tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases for each satellite system
    suite.addTests(loader.loadTestsFromTestCase(TestRemusSatelliteControl))
    suite.addTests(loader.loadTestsFromTestCase(TestSpicaNavigationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestPolarisCommunicationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestVegaDataStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestDenebTelemetrySystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAntaresSynchronization))
    suite.addTests(loader.loadTestsFromTestCase(TestRigelAdvancedControl))

    return suite


def run_tests():
    """Run all tests and return results"""
    print("Running Satellite Control System Unit Tests")
    print("=" * 50)

    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    print(f"Test Results: {result.testsRun} tests run")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed or had errors.")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
