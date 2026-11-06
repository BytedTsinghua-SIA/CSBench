"""
Unit tests for fit_scaling_laws.py.
"""

from unittest.mock import Mock

import pytest

from api_client import TrainingAPIClient
from fit_scaling_laws import ScalingLawFitter, power_law, save_results
from utils import estimate_parameters, compute_dataset_size


class TestPowerLaw:
    """Test cases for power_law function."""
    
    def test_power_law_basic(self):
        """Test basic power law calculation."""
        import numpy as np
        x = np.array([1.0, 2.0, 4.0])
        a = 2.0
        b = 3.0
        
        result = power_law(x, a, b)
        expected = 2.0 * np.power(x, 3.0)
        
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_power_law_returns_array(self):
        """Test that power_law returns numpy array."""
        import numpy as np
        x = np.array([1.0, 2.0])
        result = power_law(x, 1.0, 2.0)
        assert isinstance(result, np.ndarray)


class TestScalingLawFitterInit:
    """Test cases for ScalingLawFitter initialization."""
    
    def test_init_stores_api_client(self):
        """Test that API client is stored correctly."""
        mock_client = Mock(spec=TrainingAPIClient)
        fitter = ScalingLawFitter(mock_client)
        
        assert fitter.api_client == mock_client
        assert fitter.experimental_runs == []


class TestScalingLawFitterFitIsoflopsScalingLaw:
    """Test cases for fit_isoflops_scaling_law method."""
    
    def test_fit_requires_experimental_runs(self):
        """Test that fitting requires experimental runs."""
        mock_client = Mock(spec=TrainingAPIClient)
        fitter = ScalingLawFitter(mock_client)
        
        with pytest.raises(ValueError, match="No experimental runs"):
            fitter.fit_isoflops_scaling_law()
    
    def test_fit_returns_function_and_params(self):
        """Test that fitting returns prediction function and parameters."""
        mock_client = Mock(spec=TrainingAPIClient)
        fitter = ScalingLawFitter(mock_client)
        
        # Add sample experimental runs
        fitter.experimental_runs = [
            {
                "train_flops": int(1e16),
                "num_parameters": 1e8,
                "dataset_size": 1e10,
                "loss": 5.5
            },
            {
                "train_flops": int(1e16),
                "num_parameters": 2e8,
                "dataset_size": 5e9,
                "loss": 5.0
            },
            {
                "train_flops": int(3e16),
                "num_parameters": 3e8,
                "dataset_size": 1.67e10,
                "loss": 4.8
            }
        ]
        
        prediction_func, fit_info = fitter.fit_isoflops_scaling_law()
        
        assert callable(prediction_func)
        assert "a_N" in fit_info
        assert "b_N" in fit_info
        assert "a_D" in fit_info
        assert "b_D" in fit_info
        assert "compute_budgets" in fit_info
    
    def test_fit_groups_by_budget(self):
        """Test that fitting groups runs by compute budget."""
        mock_client = Mock(spec=TrainingAPIClient)
        fitter = ScalingLawFitter(mock_client)
        
        fitter.experimental_runs = [
            {
                "train_flops": int(1e16),
                "num_parameters": 1e8,
                "dataset_size": 1e10,
                "loss": 5.5
            },
            {
                "train_flops": int(1e16),
                "num_parameters": 2e8,
                "dataset_size": 5e9,
                "loss": 5.0  # Lower loss, should be selected
            },
            {
                "train_flops": int(3e16),
                "num_parameters": 3e8,
                "dataset_size": 1.67e10,
                "loss": 4.8
            }
        ]
        
        prediction_func, fit_info = fitter.fit_isoflops_scaling_law()
        
        # Should have 2 unique budgets
        assert len(fit_info["compute_budgets"]) == 2
        # For budget 1e16, should select run with loss 5.0 (lower)
        assert fit_info["optimal_parameters"][0] == 2e8
    
    def test_prediction_function_works(self):
        """Test that prediction function produces reasonable outputs."""
        mock_client = Mock(spec=TrainingAPIClient)
        fitter = ScalingLawFitter(mock_client)
        
        fitter.experimental_runs = [
            {
                "train_flops": int(1e16),
                "num_parameters": 1e8,
                "dataset_size": 1e10,
                "loss": 5.5
            },
            {
                "train_flops": int(3e16),
                "num_parameters": 2e8,
                "dataset_size": 2.5e10,
                "loss": 4.8
            }
        ]
        
        prediction_func, _ = fitter.fit_isoflops_scaling_law()
        
        # Test prediction for a target budget
        N_pred, D_pred, loss_pred = prediction_func(2e16)
        
        assert N_pred > 0
        assert D_pred > 0
        assert loss_pred > 0


class TestScalingLawFitterFindOptimalHyperparameters:
    """Test cases for find_optimal_hyperparameters method."""
    
    def test_find_optimal_requires_prediction_func(self):
        """Test that finding optimal hyperparameters requires prediction function."""
        mock_client = Mock(spec=TrainingAPIClient)
        fitter = ScalingLawFitter(mock_client)
        
        # Create a simple prediction function
        def pred_func(C):
            import numpy as np
            return 1e8, 1e10, 5.0
        
        result = fitter.find_optimal_hyperparameters(1e19, pred_func)
        
        assert "predicted_N" in result
        assert "predicted_D" in result
        assert "predicted_loss" in result
        assert "recommended_hyperparameters" in result
    
    def test_find_optimal_finds_closest_config(self):
        """Test that method finds closest configuration from experimental runs."""
        mock_client = Mock(spec=TrainingAPIClient)
        fitter = ScalingLawFitter(mock_client)
        
        # Add experimental runs
        fitter.experimental_runs = [
            {
                "num_parameters": 1e8,
                "dataset_size": 1e10,
                "d_model": 512,
                "num_layers": 12,
                "num_heads": 8,
                "batch_size": 128,
                "learning_rate": 1e-3,
                "train_flops": int(1e16),
                "loss": 5.5
            },
            {
                "num_parameters": 2e8,
                "dataset_size": 2e10,
                "d_model": 768,
                "num_layers": 16,
                "num_heads": 12,
                "batch_size": 256,
                "learning_rate": 3e-4,
                "train_flops": int(2e16),
                "loss": 5.0
            }
        ]
        
        # Create prediction function that predicts values close to first run
        def pred_func(C):
            return 1.1e8, 1.1e10, 5.0
        
        result = fitter.find_optimal_hyperparameters(1e19, pred_func)
        
        assert result["best_match"] is not None
        assert result["recommended_hyperparameters"] is not None
    
    def test_find_optimal_with_empty_runs(self):
        """Test finding optimal when no experimental runs available."""
        mock_client = Mock(spec=TrainingAPIClient)
        fitter = ScalingLawFitter(mock_client)
        fitter.experimental_runs = []
        
        def pred_func(C):
            return 1e8, 1e10, 5.0
        
        result = fitter.find_optimal_hyperparameters(1e19, pred_func)
        
        # Should still return structure, but best_match might be None
        assert "recommended_hyperparameters" in result


class TestSaveResults:
    """Test cases for save_results function."""
    
    def test_save_results_creates_file(self):
        """Test that save_results creates output file."""
        import tempfile
        import json
        import os
        
        test_data = {
            "key1": "value1",
            "key2": 123
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            save_results(test_data, temp_path)
            
            assert os.path.exists(temp_path)
            
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
                assert loaded_data == test_data
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_results_formats_json(self):
        """Test that save_results formats JSON correctly."""
        import tempfile
        import json
        import os
        
        test_data = {"nested": {"key": "value"}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            save_results(test_data, temp_path)
            
            with open(temp_path, 'r') as f:
                content = f.read()
                # Should be valid JSON
                loaded = json.loads(content)
                assert loaded == test_data
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

