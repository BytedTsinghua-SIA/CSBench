"""
Unit tests for chinchilla_isoflops.py functions.
"""

import json
import tempfile
from pathlib import Path
import pytest
import numpy as np
from chinchilla_isoflops import (
    load_isoflops_data,
    find_optimal_points,
    power_law,
    fit_scaling_law,
    plot_model_scaling_law,
    plot_dataset_scaling_law
)


class TestLoadIsoflopsData:
    """Test cases for load_isoflops_data function."""
    
    def test_load_valid_json(self):
        """Test loading valid JSON data."""
        test_data = [
            {
                "parameters": 50000000,
                "compute_budget": 6e18,
                "final_loss": 7.2
            },
            {
                "parameters": 100000000,
                "compute_budget": 6e18,
                "final_loss": 6.5
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = load_isoflops_data(temp_path)
            assert len(result) == 2
            assert result[0]["parameters"] == 50000000
            assert result[1]["final_loss"] == 6.5
        finally:
            Path(temp_path).unlink()
    
    def test_load_empty_list(self):
        """Test loading empty JSON array."""
        test_data = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            result = load_isoflops_data(temp_path)
            assert result == []
        finally:
            Path(temp_path).unlink()


class TestFindOptimalPoints:
    """Test cases for find_optimal_points function."""
    
    def test_single_budget_single_run(self):
        """Test with single budget and single run."""
        data = [
            {
                "parameters": 50000000,
                "compute_budget": 6e18,
                "final_loss": 7.2
            }
        ]
        
        budgets, params, datasets = find_optimal_points(data)
        
        assert len(budgets) == 1
        assert budgets[0] == 6e18
        assert params[0] == 50000000
        assert abs(datasets[0] - (6e18 / (6 * 50000000))) < 1e-6
    
    def test_single_budget_multiple_runs(self):
        """Test finding minimum loss for single budget with multiple runs."""
        data = [
            {
                "parameters": 50000000,
                "compute_budget": 6e18,
                "final_loss": 7.2
            },
            {
                "parameters": 100000000,
                "compute_budget": 6e18,
                "final_loss": 6.5
            },
            {
                "parameters": 150000000,
                "compute_budget": 6e18,
                "final_loss": 6.8
            }
        ]
        
        budgets, params, datasets = find_optimal_points(data)
        
        assert len(budgets) == 1
        assert params[0] == 100000000
        assert abs(datasets[0] - (6e18 / (6 * 100000000))) < 1e-6
    
    def test_multiple_budgets(self):
        """Test with multiple compute budgets."""
        data = [
            {
                "parameters": 50000000,
                "compute_budget": 6e18,
                "final_loss": 7.2
            },
            {
                "parameters": 100000000,
                "compute_budget": 1e19,
                "final_loss": 6.5
            }
        ]
        
        budgets, params, datasets = find_optimal_points(data)
        
        assert len(budgets) == 2
        assert budgets[0] == 6e18
        assert budgets[1] == 1e19
        assert len(params) == 2
        assert len(datasets) == 2
    
    def test_dataset_size_calculation(self):
        """Test that dataset size is calculated correctly."""
        data = [
            {
                "parameters": 1e8,
                "compute_budget": 6e18,
                "final_loss": 7.0
            }
        ]
        
        budgets, params, datasets = find_optimal_points(data)
        
        expected_dataset = 6e18 / (6 * 1e8)
        assert abs(datasets[0] - expected_dataset) < 1e-6
    
    def test_sorted_budgets(self):
        """Test that budgets are returned in sorted order."""
        data = [
            {
                "parameters": 100000000,
                "compute_budget": 1e19,
                "final_loss": 6.5
            },
            {
                "parameters": 50000000,
                "compute_budget": 6e18,
                "final_loss": 7.2
            }
        ]
        
        budgets, _, _ = find_optimal_points(data)
        
        assert budgets[0] < budgets[1]


class TestPowerLaw:
    """Test cases for power_law function."""
    
    def test_basic_power_law(self):
        """Test basic power law calculation."""
        x = np.array([1.0, 2.0, 3.0])
        a = 2.0
        b = 3.0
        
        result = power_law(x, a, b)
        expected = 2.0 * np.power(x, 3.0)
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_zero_exponent(self):
        """Test power law with zero exponent."""
        x = np.array([1.0, 2.0, 3.0])
        a = 5.0
        b = 0.0
        
        result = power_law(x, a, b)
        expected = np.array([5.0, 5.0, 5.0])
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_negative_exponent(self):
        """Test power law with negative exponent."""
        x = np.array([1.0, 2.0, 4.0])
        a = 1.0
        b = -1.0
        
        result = power_law(x, a, b)
        expected = np.array([1.0, 0.5, 0.25])
        
        np.testing.assert_array_almost_equal(result, expected)


class TestFitScalingLaw:
    """Test cases for fit_scaling_law function."""
    
    def test_fit_simple_power_law(self):
        """Test fitting a simple power law."""
        compute_budgets = [1e18, 3e18, 6e18, 1e19]
        optimal_values = [1e8, 3e8, 6e8, 1e9]
        
        fitted_func, (a, b) = fit_scaling_law(compute_budgets, optimal_values)
        
        assert callable(fitted_func)
        assert a > 0
        assert b > 0
    
    def test_fitted_function_produces_values(self):
        """Test that fitted function produces reasonable values."""
        compute_budgets = [1e18, 3e18, 6e18]
        optimal_values = [1e8, 2e8, 3e8]
        
        fitted_func, _ = fit_scaling_law(compute_budgets, optimal_values)
        predictions = fitted_func([2e18, 5e18])
        
        assert len(predictions) == 2
        assert all(p > 0 for p in predictions)
    
    def test_fit_returns_function_and_params(self):
        """Test that function returns both fitted function and parameters."""
        compute_budgets = [1e18, 3e18, 6e18]
        optimal_values = [1e8, 2e8, 3e8]
        
        result = fit_scaling_law(compute_budgets, optimal_values)
        
        assert len(result) == 2
        fitted_func, params = result
        assert callable(fitted_func)
        assert len(params) == 2
        assert isinstance(params[0], (int, float))
        assert isinstance(params[1], (int, float))
    
    def test_fit_with_two_points(self):
        """Test fitting with minimum number of points."""
        compute_budgets = [1e18, 3e18]
        optimal_values = [1e8, 2e8]
        
        fitted_func, (a, b) = fit_scaling_law(compute_budgets, optimal_values)
        
        assert callable(fitted_func)
        predictions = fitted_func([2e18])
        assert predictions[0] > 0
    
    def test_fit_extrapolation(self):
        """Test that fitted function can extrapolate."""
        compute_budgets = [1e18, 3e18, 6e18]
        optimal_values = [1e8, 2e8, 3e8]
        
        fitted_func, _ = fit_scaling_law(compute_budgets, optimal_values)
        extrapolation = fitted_func([1e20])
        
        assert extrapolation[0] > max(optimal_values)


class TestPlotFunctions:
    """Test cases for plotting functions."""
    
    def test_plot_model_scaling_law_executes(self):
        """Test that plot_model_scaling_law executes without error."""
        import os
        
        compute_budgets = [1e18, 3e18, 6e18]
        optimal_parameters = [1e8, 2e8, 3e8]
        
        # Create a simple fitted function
        def fitted_func(C_vals):
            return np.array(C_vals) * 1e-10
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            plot_model_scaling_law(compute_budgets, optimal_parameters, fitted_func, temp_path)
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_plot_dataset_scaling_law_executes(self):
        """Test that plot_dataset_scaling_law executes without error."""
        import os
        
        compute_budgets = [1e18, 3e18, 6e18]
        optimal_dataset_sizes = [1e10, 2e10, 3e10]
        
        # Create a simple fitted function
        def fitted_func(C_vals):
            return np.array(C_vals) * 1e-8
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            plot_dataset_scaling_law(compute_budgets, optimal_dataset_sizes, fitted_func, temp_path)
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

