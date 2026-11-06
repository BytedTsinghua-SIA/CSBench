"""
Unit tests for Alpha and Beta classes
"""
import pytest
import torch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab_three import LinearAlpha, LinearBeta


class TestLinearAlpha:
    """Test cases for LinearAlpha"""
    
    def test_call_and_dt(self):
        """Test alpha(t) = t and dt returns ones"""
        alpha = LinearAlpha()
        
        # Test linear interpolation including boundaries
        t = torch.tensor([0.0, 0.5, 1.0]).view(3, 1, 1, 1)
        result = alpha(t)
        expected = torch.tensor([0.0, 0.5, 1.0]).view(3, 1, 1, 1)
        assert torch.allclose(result, expected)
        
        # Test dt
        assert torch.allclose(alpha.dt(t), torch.ones_like(t))
        
        # Test output shape
        assert result.shape == (3, 1, 1, 1)


class TestLinearBeta:
    """Test cases for LinearBeta"""
    
    def test_call_and_dt(self):
        """Test beta(t) = 1-t and dt returns negative ones"""
        beta = LinearBeta()
        
        # Test linear decrease including boundaries
        t = torch.tensor([0.0, 0.5, 1.0]).view(3, 1, 1, 1)
        result = beta(t)
        expected = torch.tensor([1.0, 0.5, 0.0]).view(3, 1, 1, 1)
        assert torch.allclose(result, expected)
        
        # Test dt
        assert torch.allclose(beta.dt(t), -torch.ones_like(t))
        
        # Test output shape
        assert result.shape == (3, 1, 1, 1)

