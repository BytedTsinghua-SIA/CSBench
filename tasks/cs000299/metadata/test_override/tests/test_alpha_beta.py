"""
Unit tests for Problem 2.1: Implementing alpha_t and beta_t
Tests for LinearAlpha and SquareRootBeta classes
"""

import pytest
import torch
from abc import ABC


class Alpha(ABC):
    """Base class for alpha functions"""
    def __init__(self):
        assert torch.allclose(self(torch.zeros(1, 1)), torch.zeros(1, 1))
        assert torch.allclose(self(torch.ones(1, 1)), torch.ones(1, 1))
    
    def __call__(self, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError("Fill me in for Question 2.1!")


class Beta(ABC):
    """Base class for beta functions"""
    def __init__(self):
        assert torch.allclose(self(torch.zeros(1, 1)), torch.ones(1, 1))
        assert torch.allclose(self(torch.ones(1, 1)), torch.zeros(1, 1))
    
    def __call__(self, t: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError("Fill me in for Question 2.1!")


class TestLinearAlpha:
    """Tests for LinearAlpha class"""
    
    def test_alpha_at_zero(self):
        """Test that alpha(0) = 0"""
        alpha = LinearAlpha()
        t = torch.zeros(1, 1)
        result = alpha(t)
        assert torch.allclose(result, torch.zeros(1, 1))
    
    def test_alpha_at_one(self):
        """Test that alpha(1) = 1"""
        alpha = LinearAlpha()
        t = torch.ones(1, 1)
        result = alpha(t)
        assert torch.allclose(result, torch.ones(1, 1))
    
    def test_alpha_at_half(self):
        """Test that alpha(0.5) = 0.5"""
        alpha = LinearAlpha()
        t = torch.tensor([[0.5]])
        result = alpha(t)
        assert torch.allclose(result, torch.tensor([[0.5]]))
    
    def test_alpha_batch(self):
        """Test alpha with batch of time values"""
        alpha = LinearAlpha()
        t = torch.tensor([[0.0], [0.25], [0.5], [0.75], [1.0]])
        result = alpha(t)
        expected = torch.tensor([[0.0], [0.25], [0.5], [0.75], [1.0]])
        assert torch.allclose(result, expected)
    
    def test_alpha_monotonic(self):
        """Test that alpha is monotonic increasing"""
        alpha = LinearAlpha()
        t1 = torch.tensor([[0.3]])
        t2 = torch.tensor([[0.7]])
        result1 = alpha(t1)
        result2 = alpha(t2)
        assert (result2 > result1).all()


class TestSquareRootBeta:
    """Tests for SquareRootBeta class"""
    
    def test_beta_at_zero(self):
        """Test that beta(0) = 1"""
        beta = SquareRootBeta()
        t = torch.zeros(1, 1)
        result = beta(t)
        assert torch.allclose(result, torch.ones(1, 1), atol=1e-6)
    
    def test_beta_at_one(self):
        """Test that beta(1) = 0 (approximately)"""
        beta = SquareRootBeta()
        t = torch.ones(1, 1)
        result = beta(t)
        assert torch.allclose(result, torch.zeros(1, 1), atol=1e-6)
    
    def test_beta_at_half(self):
        """Test that beta(0.5) = sqrt(0.5)"""
        beta = SquareRootBeta()
        t = torch.tensor([[0.5]])
        result = beta(t)
        expected = torch.sqrt(torch.tensor([[0.5]]))
        assert torch.allclose(result, expected, atol=1e-6)
    
    def test_beta_batch(self):
        """Test beta with batch of time values"""
        beta = SquareRootBeta()
        t = torch.tensor([[0.0], [0.25], [0.5], [0.75], [1.0]])
        result = beta(t)
        expected = torch.sqrt(1 - t)
        assert torch.allclose(result, expected, atol=1e-6)
    
    def test_beta_monotonic(self):
        """Test that beta is monotonic decreasing"""
        beta = SquareRootBeta()
        t1 = torch.tensor([[0.3]])
        t2 = torch.tensor([[0.7]])
        result1 = beta(t1)
        result2 = beta(t2)
        assert (result1 > result2).all()
    
    def test_beta_edge_case_near_one(self):
        """Test beta near t=1 to check numerical stability"""
        beta = SquareRootBeta()
        t = torch.tensor([[0.999]])
        result = beta(t)
        expected = torch.sqrt(torch.tensor([[0.001]]))
        assert torch.allclose(result, expected, atol=1e-4)
        assert result.item() > 0  # Should be positive


# Import the actual implementations if available
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from lab_two_implementations import LinearAlpha, SquareRootBeta
except ImportError:
    # If implementations are not available, define placeholder classes
    class LinearAlpha:
        def __call__(self, t):
            raise NotImplementedError("Fill me in for Question 2.1!")
    
    class SquareRootBeta:
        def __call__(self, t):
            raise NotImplementedError("Fill me in for Question 2.1!")

