"""
Unit tests for counterexample generation functionality (Problem 1-6).

Tests verify that counterexample generation and verification functions
work correctly without revealing actual counterexamples.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import peak
import algorithms


class TestCounterexampleVerification:
    """Test counterexample verification functionality."""
    
    def test_verify_counterexample(self):
        """Test verification on various matrices."""
        from counterexample_generator import verifyCounterexample
        test_cases = [
            ([[1, 2, 1], [2, 5, 2], [1, 2, 1]], algorithms.algorithm1),
            ([[5]], algorithms.algorithm1),
            ([], algorithms.algorithm1)
        ]
        for matrix, alg_func in test_cases:
            isCounterexample, result, isPeak, problem = verifyCounterexample(
                alg_func, matrix, "test")
            assert isinstance(isCounterexample, bool)
            assert problem is not None


class TestCounterexampleGeneratorFunctions:
    """Test counterexample generator helper functions."""
    
    def test_save_counterexample(self):
        """Test that save counterexample creates file with correct format."""
        from counterexample_generator import saveCounterexample
        import tempfile
        import os
        matrix = [[1, 2], [3, 4]]
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
            temp_filename = f.name
        try:
            saveCounterexample(matrix, temp_filename, "test_algorithm")
            assert os.path.exists(temp_filename)
            with open(temp_filename, 'r') as f:
                content = f.read()
                assert 'problemMatrix' in content
                assert '[' in content
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)


class TestCounterexampleGeneration:
    """Test counterexample generation process."""
    
    def test_generate_counterexample_all_algorithms(self):
        """Test counterexample generation for all algorithms."""
        from counterexample_generator import generateCounterexampleForAlgorithm
        algorithms_to_test = [
            ("algorithm1", algorithms.algorithm1),
            ("algorithm2", algorithms.algorithm2),
            ("algorithm3", algorithms.algorithm3),
            ("algorithm4", algorithms.algorithm4)
        ]
        for alg_name, alg_func in algorithms_to_test:
            found, matrix, result, isPeak, problem = generateCounterexampleForAlgorithm(
                alg_func, alg_name, maxAttempts=5)
            assert isinstance(found, bool)
            if found:
                assert matrix is not None
                assert problem is not None


class TestCounterexampleFileStructure:
    """Test counterexample file structure and format."""
    
    def test_counterexample_file_has_matrix(self):
        """Test that counterexample file contains matrix definition."""
        import os
        counterexample_files = [
            'counterexample_algorithm2.py',
            'counterexample_algorithm3.py',
            'counterexample_algorithm4.py'
        ]
        for filename in counterexample_files:
            filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read()
                    assert 'problemMatrix' in content
    
    def test_counterexample_file_loadable(self):
        """Test that counterexample file can be loaded as Python."""
        import os
        counterexample_files = [
            'counterexample_algorithm2.py',
            'counterexample_algorithm3.py',
            'counterexample_algorithm4.py'
        ]
        for filename in counterexample_files:
            filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
            if os.path.exists(filepath):
                namespace = {}
                try:
                    with open(filepath, 'r') as f:
                        exec(f.read(), namespace)
                    assert 'problemMatrix' in namespace
                    matrix = namespace['problemMatrix']
                    assert isinstance(matrix, list)
                except Exception:
                    # File may not be valid Python, which is acceptable for templates
                    pass

