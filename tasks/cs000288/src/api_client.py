"""
API Client for Training Loss Query Service

This module provides a client for interacting with the training API
to query training losses for different model configurations.
"""

import requests
from typing import Dict, List, Optional


class TrainingAPIClient:
    """Client for the training API."""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API (e.g., "http://hyperturing.stanford.edu:8000")
            api_key: Your API key string
        """
        pass
    
    def query_loss(
        self,
        d_model: int,
        num_layers: int,
        num_heads: int,
        batch_size: int,
        learning_rate: float,
        train_flops: int
    ) -> Dict:
        """
        Query the training loss for a given configuration.
        
        Args:
            d_model: Integer in [64, 1024]
            num_layers: Integer in [2, 24]
            num_heads: Integer in [2, 16]
            batch_size: Integer, one of {128, 256}
            learning_rate: Float in [1e-4, 1e-3]
            train_flops: Integer, one of the allowed FLOPs values
        
        Returns:
            Dictionary with 'loss' and 'total_flops_used' keys
        """
        pass
    
    def get_total_flops_used(self) -> float:
        """
        Get the total FLOPs used by all queries with this API key.
        
        Returns:
            Total FLOPs used as a float
        """
        pass
    
    def get_previous_runs(self) -> List[Dict]:
        """
        Get all previous runs queried with this API key.
        
        Returns:
            List of dictionaries containing previous run configurations and results
        """
        pass
