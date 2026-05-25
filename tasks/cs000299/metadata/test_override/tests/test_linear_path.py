"""
Unit tests for Problem 4.1: Linear Conditional Probability Path
Tests for LinearConditionalProbabilityPath methods
"""

import pytest
import torch
from unittest.mock import Mock


class MockSimpleDistribution:
    """Mock simple distribution"""
    def __init__(self, dim=2):
        self.dim = dim
    
    def sample(self, num_samples):
        return torch.randn(num_samples, self.dim)


class MockDataDistribution:
    """Mock data distribution"""
    def __init__(self, dim=2):
        self.dim = dim
    
    def sample(self, num_samples):
        return torch.randn(num_samples, self.dim) * 2.0 + 1.0


class TestLinearSampleConditionalPath:
    """Tests for LinearConditionalProbabilityPath.sample_conditional_path"""
    
    def test_sample_conditional_path_shape(self):
        """Test that output has correct shape"""
        path = self._create_path()
        z = torch.randn(10, 2)
        t = torch.rand(10, 1)
        result = path.sample_conditional_path(z, t)
        assert result.shape == (10, 2)
    
    def test_sample_conditional_path_at_t_zero(self):
        """Test sampling at t=0 (should be from p_simple)"""
        path = self._create_path()
        z = torch.ones(100, 2) * 5.0  # Large z
        t = torch.zeros(100, 1)
        result = path.sample_conditional_path(z, t)
        # At t=0, should be from p_simple (N(0, I))
        mean = result.mean(dim=0)
        assert torch.allclose(mean, torch.zeros(2), atol=0.3)
    
    def test_sample_conditional_path_at_t_one(self):
        """Test sampling at t=1 (should be z)"""
        path = self._create_path()
        z = torch.ones(10, 2) * 3.0
        t = torch.ones(10, 1)
        result = path.sample_conditional_path(z, t)
        # At t=1, should be exactly z
        assert torch.allclose(result, z, atol=1e-5)
    
    def test_sample_conditional_path_interpolation(self):
        """Test that path interpolates between x0 and z"""
        path = self._create_path()
        z = torch.tensor([[2.0, 2.0]])
        t = torch.tensor([[0.5]])
        
        # Run multiple times to get average
        results = []
        for _ in range(100):
            result = path.sample_conditional_path(z, t)
            results.append(result)
        mean_result = torch.stack(results).mean(dim=0)
        
        # Mean should be between 0 (p_simple mean) and z
        assert (mean_result > 0).all()
        assert (mean_result < z).all()
    
    def test_sample_conditional_path_deterministic_at_endpoints(self):
        """Test that endpoints are deterministic"""
        path = self._create_path()
        z = torch.tensor([[1.0, 2.0]])
        
        # At t=1, should always be z
        t_one = torch.ones(1, 1)
        result1 = path.sample_conditional_path(z, t_one)
        result2 = path.sample_conditional_path(z, t_one)
        assert torch.allclose(result1, result2)
        assert torch.allclose(result1, z)
    
    def test_sample_conditional_path_batch(self):
        """Test with batch of different t values"""
        path = self._create_path()
        z = torch.randn(5, 2)
        t = torch.tensor([[0.0], [0.25], [0.5], [0.75], [1.0]])
        result = path.sample_conditional_path(z, t)
        assert result.shape == (5, 2)
    
    def _create_path(self):
        """Helper to create a path instance"""
        try:
            from lab_two_implementations import LinearConditionalProbabilityPath
            p_simple = MockSimpleDistribution(dim=2)
            p_data = MockDataDistribution(dim=2)
            return LinearConditionalProbabilityPath(p_simple, p_data)
        except (ImportError, AttributeError):
            class MockPath:
                def __init__(self, p_simple, p_data):
                    self.p_simple = p_simple
                    self.p_data = p_data
                
                def sample_conditional_path(self, z, t):
                    raise NotImplementedError("Fill me in for Question 4.1!")
            return MockPath(MockSimpleDistribution(), MockDataDistribution())


class TestLinearConditionalVectorField:
    """Tests for LinearConditionalProbabilityPath.conditional_vector_field"""
    
    def test_conditional_vector_field_shape(self):
        """Test that output has correct shape"""
        path = self._create_path()
        x = torch.randn(5, 2)
        z = torch.randn(5, 2)
        t = torch.rand(5, 1)
        result = path.conditional_vector_field(x, z, t)
        assert result.shape == (5, 2)
    
    def test_conditional_vector_field_formula(self):
        """Test that vector field follows formula u_t(x|z) = (z-x)/(1-t)"""
        path = self._create_path()
        x = torch.tensor([[1.0, 1.0]])
        z = torch.tensor([[3.0, 3.0]])
        t = torch.tensor([[0.5]])
        result = path.conditional_vector_field(x, z, t)
        expected = (z - x) / (1 - 0.5)
        assert torch.allclose(result, expected, atol=1e-5)
    
    def test_conditional_vector_field_at_t_zero(self):
        """Test vector field at t=0"""
        path = self._create_path()
        x = torch.tensor([[1.0, 2.0]])
        z = torch.tensor([[3.0, 4.0]])
        t = torch.zeros(1, 1)
        result = path.conditional_vector_field(x, z, t)
        expected = (z - x) / 1.0
        assert torch.allclose(result, expected, atol=1e-5)
    
    def test_conditional_vector_field_near_t_one(self):
        """Test vector field near t=1 (edge case)"""
        path = self._create_path()
        x = torch.tensor([[1.0, 1.0]])
        z = torch.tensor([[2.0, 2.0]])
        t = torch.tensor([[0.999]])
        result = path.conditional_vector_field(x, z, t)
        # Should be finite despite division by small number
        assert torch.isfinite(result).all()
        # Should point in direction of (z-x)
        direction = result / (torch.norm(result) + 1e-8)
        expected_direction = (z - x) / (torch.norm(z - x) + 1e-8)
        assert torch.allclose(direction, expected_direction, atol=0.1)
    
    def test_conditional_vector_field_batch(self):
        """Test with batch"""
        path = self._create_path()
        x = torch.randn(10, 2)
        z = torch.randn(10, 2)
        t = torch.rand(10, 1) * 0.99  # Avoid t=1
        result = path.conditional_vector_field(x, z, t)
        assert result.shape == (10, 2)
        assert torch.isfinite(result).all()
    
    def test_conditional_vector_field_zero_when_x_equals_z(self):
        """Test that vector field is zero when x=z"""
        path = self._create_path()
        x = torch.tensor([[2.0, 3.0]])
        z = torch.tensor([[2.0, 3.0]])  # Same as x
        t = torch.tensor([[0.5]])
        result = path.conditional_vector_field(x, z, t)
        assert torch.allclose(result, torch.zeros_like(result), atol=1e-5)
    
    def _create_path(self):
        """Helper to create a path instance"""
        try:
            from lab_two_implementations import LinearConditionalProbabilityPath
            p_simple = MockSimpleDistribution(dim=2)
            p_data = MockDataDistribution(dim=2)
            return LinearConditionalProbabilityPath(p_simple, p_data)
        except (ImportError, AttributeError):
            class MockPath:
                def __init__(self, p_simple, p_data):
                    self.p_simple = p_simple
                    self.p_data = p_data
                
                def conditional_vector_field(self, x, z, t):
                    raise NotImplementedError("Fill me in for Question 4.1!")
            return MockPath(MockSimpleDistribution(), MockDataDistribution())

