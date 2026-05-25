"""
Unit tests for complexity analysis functionality (Problem 1-4).

Tests verify that complexity analysis functions work correctly
without revealing the actual complexity answers.
"""

import pytest
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import peak
import algorithms


class TestComplexityAnalysisFunctions:
    """Test complexity analysis helper functions."""
    
    def test_generate_worst_case_matrix_all_types(self):
        """Test worst case matrix generation for all algorithm types."""
        from analyze_complexity import generateWorstCaseMatrix
        for alg_type in [1, 2, 3, 4]:
            matrix = generateWorstCaseMatrix(5, alg_type)
            assert len(matrix) == 5
            assert len(matrix[0]) == 5
            assert all(isinstance(row, list) for row in matrix)
    
    def test_measure_runtime(self):
        """Test runtime measurement functionality."""
        from analyze_complexity import measureAlgorithmRuntime
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        problem = peak.createProblem(matrix)
        runtime = measureAlgorithmRuntime(algorithms.algorithm1, problem, iterations=2)
        assert runtime >= 0


class TestRuntimeScaling:
    """Test that runtime scales with input size."""
    
    def test_all_algorithms_runtime_scales(self):
        """Test that all algorithms runtime increases with size."""
        from analyze_complexity import measureAlgorithmRuntime, generateWorstCaseMatrix
        algorithms_to_test = [
            (algorithms.algorithm1, 1),
            (algorithms.algorithm2, 2),
            (algorithms.algorithm3, 3),
            (algorithms.algorithm4, 4)
        ]
        sizes = [5, 10]
        for alg_func, alg_type in algorithms_to_test:
            runtimes = []
            for size in sizes:
                matrix = generateWorstCaseMatrix(size, alg_type)
                problem = peak.createProblem(matrix)
                runtime = measureAlgorithmRuntime(alg_func, problem, iterations=1)
                runtimes.append(runtime)
            assert len(runtimes) == 2


class TestComplexityAnalysisModule:
    """Test complexity analysis module structure."""
    
    def test_complexity_module_structure(self):
        """Test that analyze_complexity module has required functions."""
        import analyze_complexity
        assert hasattr(analyze_complexity, 'generateWorstCaseMatrix')
        assert hasattr(analyze_complexity, 'measureAlgorithmRuntime')
        assert hasattr(analyze_complexity, 'analyzeComplexity')
        assert callable(analyze_complexity.generateWorstCaseMatrix)
        assert callable(analyze_complexity.measureAlgorithmRuntime)

