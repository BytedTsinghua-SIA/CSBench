"""
Unit tests for algorithm correctness (Problem 1-3).

Tests verify that algorithms return valid peaks for various input matrices.
Each test is independent and focuses on specific scenarios.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import peak
import algorithms


class TestAlgorithm1Correctness:
    """Test correctness of algorithm1."""
    
    def test_algorithm1_basic(self):
        """Test algorithm1 on basic matrices."""
        test_cases = [
            [[5]],  # Single element
            [[1, 2], [3, 4]],  # Small matrix
            [[1, 2, 1], [2, 5, 2], [1, 2, 1]]  # Center peak
        ]
        for matrix in test_cases:
            problem = peak.createProblem(matrix)
            result = algorithms.algorithm1(problem)
            assert result is not None
            assert problem.isPeak(result)


class TestAlgorithm2Correctness:
    """Test correctness of algorithm2."""
    
    def test_algorithm2_basic(self):
        """Test algorithm2 on basic matrices."""
        test_cases = [
            [[5]],  # Single element
            [[1, 2], [3, 4]],  # Small matrix
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]]  # Increasing matrix
        ]
        for matrix in test_cases:
            problem = peak.createProblem(matrix)
            result = algorithms.algorithm2(problem)
            assert result is not None
            assert problem.isPeak(result)


class TestAlgorithm3Correctness:
    """Test correctness of algorithm3."""
    
    def test_algorithm3_basic(self):
        """Test algorithm3 on basic matrices."""
        test_cases = [
            [[5]],  # Single element
            [[1, 2], [3, 4]],  # Small matrix
            [[5, 2, 5], [2, 1, 2], [5, 2, 5]]  # Multiple peaks
        ]
        for matrix in test_cases:
            problem = peak.createProblem(matrix)
            result = algorithms.algorithm3(problem)
            assert result is not None
            assert problem.isPeak(result)


class TestAlgorithm4Correctness:
    """Test correctness of algorithm4."""
    
    def test_algorithm4_basic(self):
        """Test algorithm4 on basic matrices."""
        test_cases = [
            [[5]],  # Single element
            [[1, 2], [3, 4]],  # Small matrix
            [[10, 5], [5, 3]]  # Edge peak
        ]
        for matrix in test_cases:
            problem = peak.createProblem(matrix)
            result = algorithms.algorithm4(problem)
            assert result is not None
            assert problem.isPeak(result)


class TestAlgorithmsEdgeCases:
    """Test all algorithms on edge cases."""
    
    def test_all_algorithms_empty_matrix(self):
        """Test all algorithms handle empty matrix."""
        matrix = []
        problem = peak.createProblem(matrix)
        for alg_name, alg_func in [
            ("algorithm1", algorithms.algorithm1),
            ("algorithm2", algorithms.algorithm2),
            ("algorithm3", algorithms.algorithm3),
            ("algorithm4", algorithms.algorithm4)
        ]:
            result = alg_func(problem)
            assert result is None
    
    def test_all_algorithms_single_row(self):
        """Test all algorithms on single row matrix."""
        matrix = [[1, 5, 3, 2, 4]]
        problem = peak.createProblem(matrix)
        for alg_name, alg_func in [
            ("algorithm1", algorithms.algorithm1),
            ("algorithm2", algorithms.algorithm2),
            ("algorithm3", algorithms.algorithm3),
            ("algorithm4", algorithms.algorithm4)
        ]:
            result = alg_func(problem)
            assert result is not None
            assert problem.isPeak(result)
    
    def test_all_algorithms_single_column(self):
        """Test all algorithms on single column matrix."""
        matrix = [[1], [5], [3], [2], [4]]
        problem = peak.createProblem(matrix)
        for alg_name, alg_func in [
            ("algorithm1", algorithms.algorithm1),
            ("algorithm2", algorithms.algorithm2),
            ("algorithm3", algorithms.algorithm3),
            ("algorithm4", algorithms.algorithm4)
        ]:
            result = alg_func(problem)
            assert result is not None
            assert problem.isPeak(result)
    
    def test_all_algorithms_uniform_matrix(self):
        """Test all algorithms on uniform matrix."""
        matrix = [[5, 5, 5], [5, 5, 5], [5, 5, 5]]
        problem = peak.createProblem(matrix)
        for alg_name, alg_func in [
            ("algorithm1", algorithms.algorithm1),
            ("algorithm2", algorithms.algorithm2),
            ("algorithm3", algorithms.algorithm3),
            ("algorithm4", algorithms.algorithm4)
        ]:
            result = alg_func(problem)
            assert result is not None
            assert problem.isPeak(result)

