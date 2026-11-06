"""
Unit tests for api_client.py.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from api_client import TrainingAPIClient


class TestTrainingAPIClientInit:
    """Test cases for TrainingAPIClient initialization."""
    
    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from base_url."""
        client = TrainingAPIClient("http://example.com/", "test_key")
        assert client.base_url == "http://example.com"
    
    def test_init_preserves_url_without_slash(self):
        """Test that URL without trailing slash is preserved."""
        client = TrainingAPIClient("http://example.com", "test_key")
        assert client.base_url == "http://example.com"
    
    def test_init_stores_api_key(self):
        """Test that API key is stored correctly."""
        client = TrainingAPIClient("http://example.com", "test_key_123")
        assert client.api_key == "test_key_123"


class TestTrainingAPIClientQueryLoss:
    """Test cases for query_loss method."""
    
    @patch('api_client.requests.get')
    def test_query_loss_success(self, mock_get):
        """Test successful loss query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"loss": 5.5, "total_flops_used": 1e16}
        mock_get.return_value = mock_response
        
        client = TrainingAPIClient("http://example.com", "test_key")
        result = client.query_loss(
            d_model=512,
            num_layers=12,
            num_heads=8,
            batch_size=128,
            learning_rate=1e-3,
            train_flops=int(1e16)
        )
        
        assert result["loss"] == 5.5
        assert result["total_flops_used"] == 1e16
        mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_query_loss_404_raises_value_error(self, mock_get):
        """Test that 404 status code raises ValueError."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Invalid d_model"}
        mock_get.return_value = mock_response
        
        client = TrainingAPIClient("http://example.com", "test_key")
        
        with pytest.raises(ValueError, match="Invalid configuration"):
            client.query_loss(
                d_model=512,
                num_layers=12,
                num_heads=8,
                batch_size=128,
                learning_rate=1e-3,
                train_flops=int(1e16)
            )
    
    @patch('api_client.requests.get')
    def test_query_loss_passes_correct_parameters(self, mock_get):
        """Test that correct parameters are passed to API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"loss": 5.5, "total_flops_used": 1e16}
        mock_get.return_value = mock_response
        
        client = TrainingAPIClient("http://example.com", "test_key")
        client.query_loss(
            d_model=256,
            num_layers=8,
            num_heads=4,
            batch_size=256,
            learning_rate=3e-4,
            train_flops=int(1e15)
        )
        
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://example.com/loss"
        params = call_args[1]["params"]
        assert params["d_model"] == 256
        assert params["num_layers"] == 8
        assert params["num_heads"] == 4
        assert params["batch_size"] == 256
        assert params["learning_rate"] == 3e-4
        assert params["train_flops"] == int(1e15)
        assert params["api_key"] == "test_key"


class TestTrainingAPIClientGetTotalFlopsUsed:
    """Test cases for get_total_flops_used method."""
    
    @patch('api_client.requests.get')
    def test_get_total_flops_used_success(self, mock_get):
        """Test successful FLOPs query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = 2e18
        mock_get.return_value = mock_response
        
        client = TrainingAPIClient("http://example.com", "test_key")
        result = client.get_total_flops_used()
        
        assert result == 2e18
        mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_get_total_flops_used_returns_float(self, mock_get):
        """Test that result is returned as float."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = 10000000000000000
        mock_get.return_value = mock_response
        
        client = TrainingAPIClient("http://example.com", "test_key")
        result = client.get_total_flops_used()
        
        assert isinstance(result, float)
        assert result == 1e16


class TestTrainingAPIClientGetPreviousRuns:
    """Test cases for get_previous_runs method."""
    
    @patch('api_client.requests.get')
    def test_get_previous_runs_success(self, mock_get):
        """Test successful previous runs query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "previous_runs": [
                {"d_model": 512, "num_layers": 12, "loss": 5.5}
            ]
        }
        mock_get.return_value = mock_response
        
        client = TrainingAPIClient("http://example.com", "test_key")
        result = client.get_previous_runs()
        
        assert len(result) == 1
        assert result[0]["d_model"] == 512
        mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_get_previous_runs_empty_list(self, mock_get):
        """Test that empty list is returned when no previous runs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"previous_runs": []}
        mock_get.return_value = mock_response
        
        client = TrainingAPIClient("http://example.com", "test_key")
        result = client.get_previous_runs()
        
        assert result == []
    
    @patch('api_client.requests.get')
    def test_get_previous_runs_missing_key(self, mock_get):
        """Test handling when previous_runs key is missing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        client = TrainingAPIClient("http://example.com", "test_key")
        result = client.get_previous_runs()
        
        assert result == []

