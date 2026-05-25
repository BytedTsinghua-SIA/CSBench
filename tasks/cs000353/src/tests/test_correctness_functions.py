"""
Unit tests for correctness testing functions (Problem 1-3).

Tests verify that correctness testing helper functions work correctly.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import peak
import algorithms


class TestCorrectnessTestFunctions:
    """Test correctness testing helper functions."""
    
    def test_correctness_functions(self):
        """Test correctness testing helper functions."""
        from test_correctness import (generateRandomMatrix, generateTestCases,
                                      testAlgorithmCorrectness)
        # Test random matrix generation
        matrix = generateRandomMatrix(5, 5, 100)
        assert len(matrix) == 5
        assert len(matrix[0]) == 5
        
        # Test test case generation
        testCases = generateTestCases()
        assert isinstance(testCases, list)
        assert len(testCases) > 0
        
        # Test algorithm correctness testing
        problem = peak.createProblem([[1, 2], [3, 4]])
        isCorrect, result, isPeak = testAlgorithmCorrectness(
            algorithms.algorithm1, problem)
        assert isinstance(isCorrect, bool)
        assert isinstance(isPeak, bool)


class TestCorrectnessModuleStructure:
    """Test correctness testing module structure."""
    
    def test_correctness_module_imports(self):
        """Test that test_correctness module can be imported."""
        import test_correctness
        assert hasattr(test_correctness, 'generateRandomMatrix')
        assert hasattr(test_correctness, 'generateTestCases')
        assert hasattr(test_correctness, 'testAlgorithmCorrectness')
        assert hasattr(test_correctness, 'testAllAlgorithms')
    
    def test_correctness_functions_are_callable(self):
        """Test that correctness functions are callable."""
        from test_correctness import (generateRandomMatrix, generateTestCases,
                                      testAlgorithmCorrectness)
        assert callable(generateRandomMatrix)
        assert callable(generateTestCases)
        assert callable(testAlgorithmCorrectness)

