"""
Unit tests for Exercise 1: Summation algorithms.
Tests sum1, sum2, sum3, and rela_error functions independently.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from julia_runner import JuliaRunner


class TestSum1(unittest.TestCase):
    """Unit tests for sum1 function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_sum1_simple_case(self):
        """Test sum1 with simple integer array."""
        x = [1.0, 2.0, 3.0]
        result = self.runner.call_sum1(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 6.0, places=10)
    
    def test_sum1_single_element(self):
        """Test sum1 with single element."""
        x = [5.0]
        result = self.runner.call_sum1(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 5.0, places=10)
    
    def test_sum1_empty_array(self):
        """Test sum1 with empty array."""
        x = []
        result = self.runner.call_sum1(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.0, places=10)
    
    def test_sum1_negative_numbers(self):
        """Test sum1 with negative numbers."""
        x = [-1.0, -2.0, 3.0]
        result = self.runner.call_sum1(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.0, places=10)
    
    def test_sum1_large_array(self):
        """Test sum1 with larger array."""
        x = [1.0] * 100
        result = self.runner.call_sum1(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 100.0, places=10)


class TestSum2(unittest.TestCase):
    """Unit tests for sum2 function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_sum2_simple_case(self):
        """Test sum2 with simple array."""
        x = [1.0, 1.0]
        result = self.runner.call_sum2(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 2.0, places=10)
    
    def test_sum2_single_element(self):
        """Test sum2 with single element."""
        x = [7.0]
        result = self.runner.call_sum2(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 7.0, places=10)
    
    def test_sum2_power_of_two_length(self):
        """Test sum2 with power of two length."""
        x = [1.0, 2.0, 3.0, 4.0]
        result = self.runner.call_sum2(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 10.0, places=10)
    
    def test_sum2_larger_array(self):
        """Test sum2 with larger power of two array."""
        x = [1.0] * 8
        result = self.runner.call_sum2(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 8.0, places=10)


class TestSum3(unittest.TestCase):
    """Unit tests for sum3 function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_sum3_small_array(self):
        """Test sum3 with small array."""
        x = [1.0, 2.0, 3.0]
        result = self.runner.call_sum3(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 6.0, places=10)
    
    def test_sum3_single_element(self):
        """Test sum3 with single element."""
        x = [9.0]
        result = self.runner.call_sum3(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 9.0, places=10)
    
    def test_sum3_medium_array(self):
        """Test sum3 with medium array."""
        x = [1.0] * 100
        result = self.runner.call_sum3(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 100.0, places=10)


class TestRelaError(unittest.TestCase):
    """Unit tests for rela_error function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_rela_error_exact_match(self):
        """Test rela_error when values match exactly."""
        result = self.runner.call_rela_error(1.0, 1.0)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.0, places=10)
    
    def test_rela_error_known_case(self):
        """Test rela_error with known values."""
        result = self.runner.call_rela_error(1.0, 1.5)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.5, places=10)
    
    def test_rela_error_small_difference(self):
        """Test rela_error with small difference."""
        result = self.runner.call_rela_error(1.0, 1.01)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.0)
        self.assertLess(result, 0.02)
    
    def test_rela_error_negative(self):
        """Test rela_error with negative approximate value."""
        result = self.runner.call_rela_error(1.0, 0.5)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.5, places=10)


if __name__ == '__main__':
    unittest.main()

