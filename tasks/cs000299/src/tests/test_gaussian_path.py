"""
Unit tests for Problem 2.2, 2.3, 2.4: Gaussian Conditional Probability Path
Tests for GaussianConditionalProbabilityPath methods
"""

import pytest
import torch
from unittest.mock import Mock, patch


class MockAlpha:
    """Mock alpha function for testing"""
    def __call__(self, t):
        return t
    
    def dt(self, t):
        return torch.ones_like(t)


class MockBeta:
    """Mock beta function for testing"""
    def __call__(self, t):
        return torch.sqrt(1 - t + 1e-8)
    
    def dt(self, t):
        return -0.5 / (torch.sqrt(1 - t) + 1e-4)


class MockSampleable:
    """Mock sampleable distribution"""
    def __init__(self, dim=2):
        self.dim = dim
    
    def sample(self, num_samples):
        return torch.randn(num_samples, self.dim)


class TestGaussianSampleConditionalPath:
    """Tests for GaussianConditionalProbabilityPath.sample_conditional_path"""
    
    def test_sample_conditional_path_shape(self):
        """Test that output has correct shape"""
        path = self._create_path()
        z = torch.randn(10, 2)
        t = torch.rand(10, 1)
        result = path.sample_conditional_path(z, t)
        assert result.shape == (10, 2)
    
    def test_sample_conditional_path_at_t_zero(self):
        """Test sampling at t=0 (should be close to N(0, I))"""
        path = self._create_path()
        z = torch.ones(1000, 2) * 5.0  # Large z value
        t = torch.zeros(1000, 1)
        result = path.sample_conditional_path(z, t)
        # At t=0, alpha=0, beta=1, so should be N(0, I)
        mean = result.mean(dim=0)
        assert torch.allclose(mean, torch.zeros(2), atol=0.2)
    
    def test_sample_conditional_path_at_t_one(self):
        """Test sampling at t=1 (should be close to z)"""
        path = self._create_path()
        z = torch.ones(100, 2) * 3.0
        t = torch.ones(100, 1)
        result = path.sample_conditional_path(z, t)
        # At t=1, alpha=1, beta=0, so should be close to z
        mean = result.mean(dim=0)
        assert torch.allclose(mean, z[0], atol=0.3)
    
    def test_sample_conditional_path_deterministic_mean(self):
        """Test that mean is deterministic (alpha_t * z)"""
        path = self._create_path()
        z = torch.tensor([[2.0, 3.0]])
        t = torch.tensor([[0.5]])
        # Run multiple times and check mean
        results = []
        for _ in range(100):
            result = path.sample_conditional_path(z, t)
            results.append(result)
        mean_result = torch.stack(results).mean(dim=0)
        expected_mean = 0.5 * z  # alpha_t = 0.5
        assert torch.allclose(mean_result, expected_mean, atol=0.2)
    
    def _create_path(self):
        """Helper to create a path instance"""
        from lab_two_implementations import GaussianConditionalProbabilityPath
        p_data = MockSampleable(dim=2)
        alpha = MockAlpha()
        beta = MockBeta()
        return GaussianConditionalProbabilityPath(p_data, alpha, beta)


class TestGaussianConditionalVectorField:
    """Tests for GaussianConditionalProbabilityPath.conditional_vector_field"""
    
    def test_conditional_vector_field_shape(self):
        """Test that output has correct shape"""
        path = self._create_path()
        x = torch.randn(5, 2)
        z = torch.randn(5, 2)
        t = torch.rand(5, 1)
        result = path.conditional_vector_field(x, z, t)
        assert result.shape == (5, 2)
    
    def test_conditional_vector_field_at_t_zero(self):
        """Test vector field at t=0"""
        path = self._create_path()
        x = torch.tensor([[1.0, 2.0]])
        z = torch.tensor([[3.0, 4.0]])
        t = torch.zeros(1, 1)
        result = path.conditional_vector_field(x, z, t)
        # At t=0: alpha=0, beta=1, dot_alpha=1, dot_beta=-0.5
        # Should not be NaN or Inf
        assert torch.isfinite(result).all()
    
    def test_conditional_vector_field_at_t_half(self):
        """Test vector field at t=0.5"""
        path = self._create_path()
        x = torch.tensor([[1.0, 1.0]])
        z = torch.tensor([[2.0, 2.0]])
        t = torch.tensor([[0.5]])
        result = path.conditional_vector_field(x, z, t)
        assert result.shape == (1, 2)
        assert torch.isfinite(result).all()
    
    def test_conditional_vector_field_near_t_one(self):
        """Test vector field near t=1 (edge case)"""
        path = self._create_path()
        x = torch.tensor([[1.0, 1.0]])
        z = torch.tensor([[2.0, 2.0]])
        t = torch.tensor([[0.999]])
        result = path.conditional_vector_field(x, z, t)
        assert torch.isfinite(result).all()
    
    def test_conditional_vector_field_batch(self):
        """Test vector field with batch"""
        path = self._create_path()
        x = torch.randn(10, 2)
        z = torch.randn(10, 2)
        t = torch.rand(10, 1)
        result = path.conditional_vector_field(x, z, t)
        assert result.shape == (10, 2)
        assert torch.isfinite(result).all()
    
    def _create_path(self):
        """Helper to create a path instance"""
        from lab_two_implementations import GaussianConditionalProbabilityPath
        p_data = MockSampleable(dim=2)
        alpha = MockAlpha()
        beta = MockBeta()
        return GaussianConditionalProbabilityPath(p_data, alpha, beta)


class TestGaussianConditionalScore:
    """Tests for GaussianConditionalProbabilityPath.conditional_score"""
    
    def test_conditional_score_shape(self):
        """Test that output has correct shape"""
        path = self._create_path()
        x = torch.randn(5, 2)
        z = torch.randn(5, 2)
        t = torch.rand(5, 1)
        result = path.conditional_score(x, z, t)
        assert result.shape == (5, 2)
    
    def test_conditional_score_at_t_zero(self):
        """Test score at t=0"""
        path = self._create_path()
        x = torch.tensor([[1.0, 2.0]])
        z = torch.tensor([[3.0, 4.0]])
        t = torch.zeros(1, 1)
        result = path.conditional_score(x, z, t)
        # At t=0: alpha=0, beta=1, so score = (0*z - x) / 1 = -x
        expected = -x
        assert torch.allclose(result, expected, atol=1e-5)
    
    def test_conditional_score_at_t_half(self):
        """Test score at t=0.5"""
        path = self._create_path()
        x = torch.tensor([[1.0, 1.0]])
        z = torch.tensor([[2.0, 2.0]])
        t = torch.tensor([[0.5]])
        result = path.conditional_score(x, z, t)
        # alpha=0.5, beta=sqrt(0.5), score = (0.5*z - x) / 0.5
        expected = (0.5 * z - x) / 0.5
        assert torch.allclose(result, expected, atol=1e-5)
    
    def test_conditional_score_near_t_one(self):
        """Test score near t=1 (edge case)"""
        path = self._create_path()
        x = torch.tensor([[1.0, 1.0]])
        z = torch.tensor([[2.0, 2.0]])
        t = torch.tensor([[0.999]])
        result = path.conditional_score(x, z, t)
        assert torch.isfinite(result).all()
    
    def test_conditional_score_batch(self):
        """Test score with batch"""
        path = self._create_path()
        x = torch.randn(10, 2)
        z = torch.randn(10, 2)
        t = torch.rand(10, 1)
        result = path.conditional_score(x, z, t)
        assert result.shape == (10, 2)
        assert torch.isfinite(result).all()
    
    def _create_path(self):
        """Helper to create a path instance"""
        from lab_two_implementations import GaussianConditionalProbabilityPath
        p_data = MockSampleable(dim=2)
        alpha = MockAlpha()
        beta = MockBeta()
        return GaussianConditionalProbabilityPath(p_data, alpha, beta)

