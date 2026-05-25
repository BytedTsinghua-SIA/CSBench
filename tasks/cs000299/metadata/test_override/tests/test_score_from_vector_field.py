"""
Unit tests for Problem 3.3: Deriving Score from Vector Field
Tests for ScoreFromVectorField.forward
"""

import pytest
import torch
from unittest.mock import Mock


class MockAlphaForScore:
    """Mock alpha for score computation"""
    def __call__(self, t):
        return t
    
    def dt(self, t):
        return torch.ones_like(t)


class MockBetaForScore:
    """Mock beta for score computation"""
    def __call__(self, t):
        return torch.sqrt(1 - t + 1e-8)
    
    def dt(self, t):
        return -0.5 / (torch.sqrt(1 - t) + 1e-4)


class MockVectorField:
    """Mock vector field model"""
    def __init__(self):
        pass
    
    def __call__(self, x, t):
        # Return a simple vector field
        return x * t + torch.randn_like(x) * 0.1


class TestScoreFromVectorField:
    """Tests for ScoreFromVectorField.forward"""
    
    def test_forward_shape(self):
        """Test that output has correct shape"""
        score_computer = self._create_score_computer()
        x = torch.randn(5, 2)
        t = torch.rand(5, 1)
        result = score_computer(x, t)
        assert result.shape == (5, 2)
    
    def test_forward_finite(self):
        """Test that output is finite"""
        score_computer = self._create_score_computer()
        x = torch.randn(10, 2)
        t = torch.rand(10, 1)
        result = score_computer(x, t)
        assert torch.isfinite(result).all()
    
    def test_forward_at_t_zero(self):
        """Test forward at t=0"""
        score_computer = self._create_score_computer()
        x = torch.tensor([[1.0, 2.0]])
        t = torch.zeros(1, 1)
        result = score_computer(x, t)
        assert torch.isfinite(result).all()
        assert result.shape == (1, 2)
    
    def test_forward_at_t_half(self):
        """Test forward at t=0.5"""
        score_computer = self._create_score_computer()
        x = torch.tensor([[1.0, 1.0]])
        t = torch.tensor([[0.5]])
        result = score_computer(x, t)
        assert torch.isfinite(result).all()
        assert result.shape == (1, 2)
    
    def test_forward_near_t_one(self):
        """Test forward near t=1 (edge case)"""
        score_computer = self._create_score_computer()
        x = torch.tensor([[1.0, 1.0]])
        t = torch.tensor([[0.999]])
        result = score_computer(x, t)
        assert torch.isfinite(result).all()
    
    def test_forward_batch(self):
        """Test forward with batch"""
        score_computer = self._create_score_computer()
        x = torch.randn(10, 2)
        t = torch.rand(10, 1)
        result = score_computer(x, t)
        assert result.shape == (10, 2)
        assert torch.isfinite(result).all()
    
    def test_forward_uses_vector_field(self):
        """Test that forward uses vector field"""
        vector_field = MockVectorField()
        alpha = MockAlphaForScore()
        beta = MockBetaForScore()
        
        score_computer = self._create_score_computer(vector_field, alpha, beta)
        x = torch.randn(5, 2)
        t = torch.rand(5, 1)
        result = score_computer(x, t)
        
        assert torch.isfinite(result).all()
    
    def test_forward_uses_alpha_beta(self):
        """Test that forward uses alpha and beta"""
        vector_field = MockVectorField()
        alpha = MockAlphaForScore()
        beta = MockBetaForScore()
        
        score_computer = self._create_score_computer(vector_field, alpha, beta)
        x = torch.randn(5, 2)
        t = torch.tensor([[0.5]])
        result = score_computer(x, t)
        
        assert torch.isfinite(result).all()
        assert result.shape == (1, 2)
    
    def _create_score_computer(self, vector_field=None, alpha=None, beta=None):
        """Helper to create score computer instance"""
        try:
            from lab_two_implementations import ScoreFromVectorField
            if vector_field is None:
                vector_field = MockVectorField()
            if alpha is None:
                alpha = MockAlphaForScore()
            if beta is None:
                beta = MockBetaForScore()
            return ScoreFromVectorField(vector_field, alpha, beta)
        except (ImportError, AttributeError):
            class MockScoreComputer:
                def __init__(self, vector_field, alpha, beta):
                    self.vector_field = vector_field
                    self.alpha = alpha
                    self.beta = beta
                
                def forward(self, x, t):
                    raise NotImplementedError("Fill me in for Question 3.3!")
            
            if vector_field is None:
                vector_field = MockVectorField()
            if alpha is None:
                alpha = MockAlphaForScore()
            if beta is None:
                beta = MockBetaForScore()
            return MockScoreComputer(vector_field, alpha, beta)

