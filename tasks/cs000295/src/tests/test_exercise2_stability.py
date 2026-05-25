"""
Unit tests for Exercise 2: Conditioning and stability.
Tests naive_phi, stable_phi, and condition_number_phi functions independently.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from julia_runner import JuliaRunner


class TestNaivePhi(unittest.TestCase):
    """Unit tests for naive_phi function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_naive_phi_zero(self):
        """Test naive_phi at x=0."""
        result = self.runner.call_naive_phi(0.0)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.0, places=10)
    
    def test_naive_phi_positive(self):
        """Test naive_phi with positive value."""
        x = 0.1
        expected = math.sqrt(1 + x) - 1
        result = self.runner.call_naive_phi(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_naive_phi_small_value(self):
        """Test naive_phi with small positive value."""
        x = 0.01
        expected = math.sqrt(1 + x) - 1
        result = self.runner.call_naive_phi(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_naive_phi_larger_value(self):
        """Test naive_phi with larger value."""
        x = 1.0
        expected = math.sqrt(1 + x) - 1
        result = self.runner.call_naive_phi(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=10)


class TestStablePhi(unittest.TestCase):
    """Unit tests for stable_phi function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_stable_phi_zero(self):
        """Test stable_phi at x=0."""
        result = self.runner.call_stable_phi(0.0)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.0, places=10)
    
    def test_stable_phi_positive(self):
        """Test stable_phi with positive value."""
        x = 0.1
        expected = x / (math.sqrt(1 + x) + 1)
        result = self.runner.call_stable_phi(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_stable_phi_small_value(self):
        """Test stable_phi with small positive value."""
        x = 0.01
        expected = x / (math.sqrt(1 + x) + 1)
        result = self.runner.call_stable_phi(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_stable_phi_equivalent_to_naive(self):
        """Test that stable_phi gives equivalent result to naive_phi."""
        x = 0.1
        naive_result = self.runner.call_naive_phi(x)
        stable_result = self.runner.call_stable_phi(x)
        self.assertIsNotNone(naive_result)
        self.assertIsNotNone(stable_result)
        # Should be mathematically equivalent
        self.assertAlmostEqual(naive_result, stable_result, places=10)


class TestConditionNumberPhi(unittest.TestCase):
    """Unit tests for condition_number_phi function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_condition_number_phi_zero(self):
        """Test condition_number_phi at x=0."""
        result = self.runner.call_condition_number_phi(0.0)
        self.assertIsNotNone(result)
        # At x=0, condition number should be 1.0
        self.assertAlmostEqual(result, 1.0, places=10)
    
    def test_condition_number_phi_positive(self):
        """Test condition_number_phi with positive value."""
        x = 0.1
        sqrt_1px = math.sqrt(1 + x)
        expected = (sqrt_1px + 1) / (2 * sqrt_1px)
        result = self.runner.call_condition_number_phi(x)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=10)
    
    def test_condition_number_phi_small_value(self):
        """Test condition_number_phi with small value."""
        x = 0.01
        result = self.runner.call_condition_number_phi(x)
        self.assertIsNotNone(result)
        # Condition number should be close to 1 for small x
        self.assertGreater(result, 0.9)
        self.assertLess(result, 1.1)
    
    def test_condition_number_phi_well_conditioned(self):
        """Test that problem is well-conditioned near zero."""
        x = 0.001
        result = self.runner.call_condition_number_phi(x)
        self.assertIsNotNone(result)
        # Well-conditioned means condition number close to 1
        self.assertGreater(result, 0.99)
        self.assertLess(result, 1.01)


if __name__ == '__main__':
    unittest.main()

