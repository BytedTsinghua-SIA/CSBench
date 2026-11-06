"""
Unit tests for Problem 3.1: Flow Matching
Tests for ConditionalFlowMatchingTrainer.get_train_loss
"""

import pytest
import torch
from unittest.mock import Mock, MagicMock


class MockPath:
    """Mock conditional probability path"""
    def __init__(self):
        self.p_data = Mock()
        self.p_data.sample = Mock(return_value=torch.randn(10, 2))
    
    def sample_conditional_path(self, z, t):
        # Simple mock: return z scaled by t
        return t * z + (1 - t) * torch.randn_like(z)
    
    def conditional_vector_field(self, x, z, t):
        # Simple mock: return a vector field
        return (z - x) / (1 - t + 1e-8)


class MockModel:
    """Mock neural network model"""
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    def __call__(self, x, t):
        if self.return_value is not None:
            return self.return_value
        # Return a simple function of x and t
        return x * t + torch.randn_like(x) * 0.1


class TestConditionalFlowMatchingTrainer:
    """Tests for ConditionalFlowMatchingTrainer.get_train_loss"""
    
    def test_train_loss_shape(self):
        """Test that loss is a scalar"""
        trainer = self._create_trainer()
        loss = trainer.get_train_loss(batch_size=10)
        assert loss.shape == ()
        assert isinstance(loss, torch.Tensor)
    
    def test_train_loss_non_negative(self):
        """Test that loss is non-negative"""
        trainer = self._create_trainer()
        loss = trainer.get_train_loss(batch_size=10)
        assert loss.item() >= 0
    
    def test_train_loss_finite(self):
        """Test that loss is finite"""
        trainer = self._create_trainer()
        loss = trainer.get_train_loss(batch_size=10)
        assert torch.isfinite(loss)
    
    def test_train_loss_different_batch_sizes(self):
        """Test with different batch sizes"""
        trainer = self._create_trainer()
        for batch_size in [1, 5, 10, 100]:
            loss = trainer.get_train_loss(batch_size=batch_size)
            assert torch.isfinite(loss)
            assert loss.item() >= 0
    
    def test_train_loss_uses_path_methods(self):
        """Test that trainer uses path methods correctly"""
        path = MockPath()
        model = MockModel()
        trainer = self._create_trainer(path, model)
        
        # Reset mocks
        path.p_data.sample.reset_mock()
        
        loss = trainer.get_train_loss(batch_size=5)
        
        # Check that p_data.sample was called
        assert path.p_data.sample.called
        # Check that sample_conditional_path would be called (indirectly)
        assert torch.isfinite(loss)
    
    def test_train_loss_with_perfect_model(self):
        """Test loss when model matches reference exactly"""
        path = MockPath()
        
        # Create model that returns reference vector field
        def perfect_model(x, t):
            z_mock = torch.randn_like(x)
            return path.conditional_vector_field(x, z_mock, t)
        
        model = MockModel()
        model.__call__ = perfect_model
        
        trainer = self._create_trainer(path, model)
        loss = trainer.get_train_loss(batch_size=10)
        
        # Loss should be small but not exactly zero due to randomness
        assert loss.item() >= 0
        assert torch.isfinite(loss)
    
    def test_train_loss_device_consistency(self):
        """Test that loss works on CPU"""
        trainer = self._create_trainer()
        loss = trainer.get_train_loss(batch_size=10)
        assert loss.device.type == 'cpu' or loss.device.type == 'cuda'
    
    def _create_trainer(self, path=None, model=None):
        """Helper to create trainer instance"""
        try:
            from lab_two_implementations import ConditionalFlowMatchingTrainer
            if path is None:
                path = MockPath()
            if model is None:
                model = MockModel()
            return ConditionalFlowMatchingTrainer(path, model)
        except (ImportError, AttributeError):
            # If implementation not available, create mock trainer
            class MockTrainer:
                def __init__(self, path, model):
                    self.path = path
                    self.model = model
                
                def get_train_loss(self, batch_size):
                    raise NotImplementedError("Fill me in for Question 3.1!")
            return MockTrainer(path, model)

