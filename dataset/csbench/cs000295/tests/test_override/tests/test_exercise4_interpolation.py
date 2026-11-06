"""
Unit tests for Exercise 4: Lagrange interpolation.
Tests lagrange_cardinal, lagrange_interpolant, and chebyshev_points functions independently.
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from julia_runner import JuliaRunner


class TestLagrangeCardinal(unittest.TestCase):
    """Unit tests for lagrange_cardinal function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_lagrange_cardinal_kronecker_delta(self):
        """Test that lagrange_cardinal satisfies Kronecker delta property."""
        t = [-1.0, 0.0, 1.0]
        # At node k (1-indexed), should equal 1
        result_k1 = self.runner.call_lagrange_cardinal(t, t[0], 1)
        result_k2 = self.runner.call_lagrange_cardinal(t, t[1], 2)
        result_k3 = self.runner.call_lagrange_cardinal(t, t[2], 3)
        
        self.assertIsNotNone(result_k1)
        self.assertIsNotNone(result_k2)
        self.assertIsNotNone(result_k3)
        self.assertAlmostEqual(result_k1, 1.0, places=10)
        self.assertAlmostEqual(result_k2, 1.0, places=10)
        self.assertAlmostEqual(result_k3, 1.0, places=10)
    
    def test_lagrange_cardinal_zero_at_other_nodes(self):
        """Test that lagrange_cardinal is zero at other nodes."""
        t = [-1.0, 0.0, 1.0]
        # Cardinal function for node 1 evaluated at node 2 should be 0
        result = self.runner.call_lagrange_cardinal(t, t[1], 1)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.0, places=10)
    
    def test_lagrange_cardinal_two_nodes(self):
        """Test lagrange_cardinal with two nodes."""
        t = [0.0, 1.0]
        result = self.runner.call_lagrange_cardinal(t, 0.5, 1)
        self.assertIsNotNone(result)
        # Should be linear interpolation weight
        self.assertGreater(result, 0.0)
        self.assertLess(result, 1.0)
    
    def test_lagrange_cardinal_interpolation_point(self):
        """Test lagrange_cardinal at interpolation point."""
        t = [-1.0, 0.0, 1.0]
        x = 0.5
        result = self.runner.call_lagrange_cardinal(t, x, 2)
        self.assertIsNotNone(result)
        # Should be a valid interpolation weight
        self.assertIsInstance(result, (int, float))


class TestLagrangeInterpolant(unittest.TestCase):
    """Unit tests for lagrange_interpolant function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_lagrange_interpolant_exact_at_nodes(self):
        """Test that interpolant matches data exactly at nodes."""
        t = [-1.0, 0.0, 1.0]
        y = [1.0, 2.0, 3.0]
        
        result_t0 = self.runner.call_lagrange_interpolant(t, y, t[0])
        result_t1 = self.runner.call_lagrange_interpolant(t, y, t[1])
        result_t2 = self.runner.call_lagrange_interpolant(t, y, t[2])
        
        self.assertIsNotNone(result_t0)
        self.assertIsNotNone(result_t1)
        self.assertIsNotNone(result_t2)
        self.assertAlmostEqual(result_t0, y[0], places=10)
        self.assertAlmostEqual(result_t1, y[1], places=10)
        self.assertAlmostEqual(result_t2, y[2], places=10)
    
    def test_lagrange_interpolant_linear_function(self):
        """Test interpolant with linear function."""
        t = [0.0, 1.0]
        y = [0.0, 1.0]
        # For linear function, interpolant should be exact
        result = self.runner.call_lagrange_interpolant(t, y, 0.5)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.5, places=10)
    
    def test_lagrange_interpolant_three_points(self):
        """Test interpolant with three interpolation points."""
        t = [-1.0, 0.0, 1.0]
        y = [2.0, 1.0, 2.0]
        result = self.runner.call_lagrange_interpolant(t, y, 0.0)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 1.0, places=10)
    
    def test_lagrange_interpolant_interpolation_property(self):
        """Test that interpolant satisfies interpolation property."""
        t = [0.0, 1.0, 2.0]
        y = [1.0, 4.0, 9.0]
        # At each node, should match exactly
        for i in range(len(t)):
            result = self.runner.call_lagrange_interpolant(t, y, t[i])
            self.assertIsNotNone(result)
            self.assertAlmostEqual(result, y[i], places=10)


class TestChebyshevPoints(unittest.TestCase):
    """Unit tests for chebyshev_points function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = JuliaRunner()
    
    def test_chebyshev_points_count(self):
        """Test that chebyshev_points returns correct number of points."""
        n = 5
        result = self.runner.call_chebyshev_points(n)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), n + 1)
    
    def test_chebyshev_points_range(self):
        """Test that chebyshev points are in [-1, 1]."""
        n = 10
        result = self.runner.call_chebyshev_points(n)
        self.assertIsNotNone(result)
        for point in result:
            self.assertGreaterEqual(point, -1.0)
            self.assertLessEqual(point, 1.0)
    
    def test_chebyshev_points_endpoints(self):
        """Test that chebyshev points include endpoints."""
        n = 5
        result = self.runner.call_chebyshev_points(n)
        self.assertIsNotNone(result)
        # Should include -1 and 1
        self.assertAlmostEqual(result[0], 1.0, places=10)
        self.assertAlmostEqual(result[-1], -1.0, places=10)
    
    def test_chebyshev_points_symmetry(self):
        """Test that chebyshev points are symmetric."""
        n = 6
        result = self.runner.call_chebyshev_points(n)
        self.assertIsNotNone(result)
        # Points should be symmetric about 0
        mid = len(result) // 2
        for i in range(mid):
            self.assertAlmostEqual(result[i], -result[-(i+1)], places=10)
    
    def test_chebyshev_points_monotonic(self):
        """Test that chebyshev points are in descending order."""
        n = 5
        result = self.runner.call_chebyshev_points(n)
        self.assertIsNotNone(result)
        for i in range(len(result) - 1):
            self.assertGreater(result[i], result[i+1])


if __name__ == '__main__':
    unittest.main()

