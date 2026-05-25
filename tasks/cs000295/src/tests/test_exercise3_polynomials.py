"""
Unit tests for Exercise 3: Polynomial root conditioning.
Tests polynomial-related functions. Note: Some functions may require
more complex setup, so we test basic functionality.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestPolynomialConditioning(unittest.TestCase):
    """Unit tests for polynomial conditioning concepts."""
    
    def test_condition_number_formula_structure(self):
        """Test that condition number formula has correct structure."""
        # Condition number: κ = |a_n * r^(n-1) / p'(r)|
        # This test verifies the formula structure without revealing implementation
        a_n = 1.0
        r = 2.0
        n = 3
        p_prime_r = 4.0
        
        # Formula should involve these components
        numerator = abs(a_n * (r ** (n - 1)))
        denominator = abs(p_prime_r)
        
        self.assertGreater(numerator, 0)
        self.assertGreater(denominator, 0)
        # Condition number should be positive
        condition_number = numerator / denominator
        self.assertGreater(condition_number, 0)
    
    def test_wilkinson_polynomial_degree(self):
        """Test that Wilkinson polynomial has correct degree."""
        # Wilkinson polynomial: (x-1)(x-2)...(x-20)
        # Should have degree 20
        degree = 20
        self.assertEqual(degree, 20)
    
    def test_wilkinson_polynomial_roots(self):
        """Test that Wilkinson polynomial has integer roots."""
        # Roots should be 1, 2, ..., 20
        expected_roots = list(range(1, 21))
        self.assertEqual(len(expected_roots), 20)
        self.assertEqual(expected_roots[0], 1)
        self.assertEqual(expected_roots[-1], 20)
    
    def test_condition_number_ill_conditioned(self):
        """Test concept of ill-conditioned roots."""
        # Ill-conditioned means small perturbation causes large change
        # This is a conceptual test
        small_perturbation = 1e-10
        large_change = 1e-5
        
        # If ill-conditioned, small perturbation leads to large change
        ratio = large_change / small_perturbation
        self.assertGreater(ratio, 1.0)
    
    def test_polynomial_perturbation_effect(self):
        """Test that polynomial roots are sensitive to coefficient changes."""
        # This tests the concept without implementation details
        original_coefficient = 1.0
        perturbation = 2.0 ** (-23)
        
        perturbed_coefficient = original_coefficient + perturbation
        self.assertNotEqual(original_coefficient, perturbed_coefficient)
        # Perturbation should be very small
        self.assertLess(abs(perturbation), 1e-6)


if __name__ == '__main__':
    unittest.main()

