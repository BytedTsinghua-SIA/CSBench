"""
Unit tests for utils.py functions.
"""

import pytest
from utils import estimate_parameters, compute_dataset_size


class TestEstimateParameters:
    """Test cases for estimate_parameters function."""
    
    def test_basic_calculation(self):
        """Test basic parameter estimation."""
        result = estimate_parameters(num_layers=2, d_model=64)
        expected = 12 * 2 * (64 ** 2)
        assert result == expected
    
    def test_single_layer(self):
        """Test with minimum number of layers."""
        result = estimate_parameters(num_layers=1, d_model=128)
        expected = 12 * 1 * (128 ** 2)
        assert result == expected
    
    def test_large_model(self):
        """Test with large model dimensions."""
        result = estimate_parameters(num_layers=24, d_model=1024)
        expected = 12 * 24 * (1024 ** 2)
        assert result == expected
    
    def test_small_dimensions(self):
        """Test with minimum dimensions."""
        result = estimate_parameters(num_layers=2, d_model=64)
        assert result > 0
    
    def test_zero_layers_raises_no_exception(self):
        """Test edge case with zero layers."""
        result = estimate_parameters(num_layers=0, d_model=64)
        assert result == 0


class TestComputeDatasetSize:
    """Test cases for compute_dataset_size function."""
    
    def test_basic_calculation(self):
        """Test basic dataset size calculation."""
        compute_budget = 6e18
        num_parameters = 1e8
        result = compute_dataset_size(compute_budget, num_parameters)
        expected = compute_budget / (6 * num_parameters)
        assert abs(result - expected) < 1e-6
    
    def test_small_budget(self):
        """Test with small compute budget."""
        compute_budget = 1e13
        num_parameters = 1e7
        result = compute_dataset_size(compute_budget, num_parameters)
        assert result > 0
    
    def test_large_budget(self):
        """Test with large compute budget."""
        compute_budget = 1e19
        num_parameters = 1e9
        result = compute_dataset_size(compute_budget, num_parameters)
        assert result > 0
    
    def test_inverse_relationship(self):
        """Test that dataset size decreases as parameters increase."""
        compute_budget = 1e18
        small_params = 1e7
        large_params = 1e8
        
        small_result = compute_dataset_size(compute_budget, small_params)
        large_result = compute_dataset_size(compute_budget, large_params)
        
        assert small_result > large_result
    
    def test_formula_consistency(self):
        """Test that C = 6 * N * D relationship holds."""
        compute_budget = 6e18
        num_parameters = 1e8
        
        dataset_size = compute_dataset_size(compute_budget, num_parameters)
        reconstructed_budget = 6 * num_parameters * dataset_size
        
        assert abs(compute_budget - reconstructed_budget) < 1e-6

