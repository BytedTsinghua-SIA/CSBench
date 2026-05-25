"""
Unit tests for GaussianConditionalProbabilityPath
"""
import pytest
import torch
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab_three import (
    GaussianConditionalProbabilityPath,
    IsotropicGaussian,
    LinearAlpha,
    LinearBeta,
    Sampleable
)


class MockDataSampler(Sampleable):
    """Mock data sampler for testing"""
    def __init__(self, shape):
        self.shape = shape
    
    def sample(self, num_samples):
        z = torch.randn(num_samples, *self.shape)
        y = torch.randint(0, 10, (num_samples,))
        return z, y


class TestGaussianConditionalProbabilityPath:
    """Test cases for GaussianConditionalProbabilityPath"""
    
    def test_initialization(self):
        """Test path initialization"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        assert path.p_data == p_data
        assert path.alpha is not None
        assert path.beta is not None
    
    def test_sample_conditioning_variable(self):
        """Test sampling conditioning variable"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        z, y = path.sample_conditioning_variable(5)
        
        assert z.shape == (5, 1, 32, 32)
        assert y.shape == (5,)
    
    def test_sample_conditional_path_at_t0(self):
        """Test sampling conditional path at t=0"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        z = torch.randn(3, 1, 32, 32)
        t = torch.zeros(3, 1, 1, 1)
        
        x = path.sample_conditional_path(z, t)
        
        assert x.shape == (3, 1, 32, 32)
        # At t=0, alpha=0, beta=1, so x = 0*z + 1*noise = noise
        # x should have similar distribution to noise (mean ~0, std ~1)
        assert torch.abs(x.mean()) < 0.5  # Mean should be close to 0
        assert 0.5 < x.std() < 2.0  # Std should be around 1
    
    def test_sample_conditional_path_at_t1(self):
        """Test sampling conditional path at t=1"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        z = torch.randn(3, 1, 32, 32)
        t = torch.ones(3, 1, 1, 1)
        
        x = path.sample_conditional_path(z, t)
        
        assert x.shape == (3, 1, 32, 32)
        # At t=1, alpha=1, beta=0, so x should be close to z (with noise)
        assert torch.allclose(x, z, atol=1.0)
    
    def test_sample_conditional_path_at_edge_times(self):
        """Test sampling conditional path at edge times (t close to 0 or 1)"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        z = torch.randn(2, 1, 32, 32)
        
        # Test t very close to 0
        t_near_zero = torch.tensor([0.001, 0.01]).view(2, 1, 1, 1)
        x_near_zero = path.sample_conditional_path(z, t_near_zero)
        assert x_near_zero.shape == (2, 1, 32, 32)
        
        # Test t very close to 1
        t_near_one = torch.tensor([0.99, 0.999]).view(2, 1, 1, 1)
        x_near_one = path.sample_conditional_path(z, t_near_one)
        assert x_near_one.shape == (2, 1, 32, 32)
    
    def test_conditional_vector_field_shape(self):
        """Test conditional vector field output shape"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        x = torch.randn(3, 1, 32, 32)
        z = torch.randn(3, 1, 32, 32)
        t = torch.rand(3, 1, 1, 1)
        
        u = path.conditional_vector_field(x, z, t)
        
        assert u.shape == (3, 1, 32, 32)
    
    def test_conditional_score_shape(self):
        """Test conditional score output shape"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        x = torch.randn(3, 1, 32, 32)
        z = torch.randn(3, 1, 32, 32)
        t = torch.rand(3, 1, 1, 1)
        
        score = path.conditional_score(x, z, t)
        
        assert score.shape == (3, 1, 32, 32)
    
    def test_conditional_score_at_edge_times(self):
        """Test conditional score at edge times (t close to 0 or 1)"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        x = torch.randn(2, 1, 32, 32)
        z = torch.randn(2, 1, 32, 32)
        
        # Test at t close to 0 (should not cause division by zero)
        t_near_zero = torch.tensor([0.001, 0.01]).view(2, 1, 1, 1)
        score = path.conditional_score(x, z, t_near_zero)
        assert score.shape == (2, 1, 32, 32)
        assert torch.all(torch.isfinite(score))
        
        # Test at t close to 1
        t_near_one = torch.tensor([0.99, 0.999]).view(2, 1, 1, 1)
        score = path.conditional_score(x, z, t_near_one)
        assert score.shape == (2, 1, 32, 32)
        assert torch.all(torch.isfinite(score))
    
    def test_sample_marginal_path(self):
        """Test sampling from marginal path"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        t = torch.rand(5, 1, 1, 1)
        x = path.sample_marginal_path(t)
        
        assert x.shape == (5, 1, 32, 32)

