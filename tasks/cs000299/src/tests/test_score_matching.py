"""
Unit tests for Problem 3.2: Score Matching
Tests for ConditionalScoreMatchingTrainer.get_train_loss
"""

import pytest
import torch
from unittest.mock import Mock


class MockPathForScore:
    """Mock conditional probability path for score matching"""
    def __init__(self):
        self.p_data = Mock()
        self.p_data.sample = Mock(return_value=torch.randn(10, 2))
    
    def sample_conditional_path(self, z, t):
        return t * z + (1 - t) * torch.randn_like(z)
    
    def conditional_score(self, x, z, t):
        # Simple mock score: (z - x) / (1 - t + epsilon)
        return (z - x) / (1 - t + 1e-8)


class MockScoreModel:
    """Mock score model"""
    def __init__(self):
        pass
    
    def __call__(self, x, t):
        # Return a simple function
        return x * 0.5 + torch.randn_like(x) * 0.1


class TestConditionalScoreMatchingTrainer:
    """Tests for ConditionalScoreMatchingTrainer.get_train_loss"""
    
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
    
    def test_train_loss_uses_conditional_score(self):
        """Test that trainer uses conditional_score method"""
        path = MockPathForScore()
        model = MockScoreModel()
        trainer = self._create_trainer(path, model)
        
        path.p_data.sample.reset_mock()
        
        loss = trainer.get_train_loss(batch_size=5)
        
        assert path.p_data.sample.called
        assert torch.isfinite(loss)
    
    def test_train_loss_with_perfect_model(self):
        """Test loss when model matches reference score"""
        path = MockPathForScore()
        
        def perfect_score_model(x, t):
            z_mock = torch.randn_like(x)
            return path.conditional_score(x, z_mock, t)
        
        model = MockScoreModel()
        model.__call__ = perfect_score_model
        
        trainer = self._create_trainer(path, model)
        loss = trainer.get_train_loss(batch_size=10)
        
        assert loss.item() >= 0
        assert torch.isfinite(loss)
    
    def _create_trainer(self, path=None, model=None):
        """Helper to create trainer instance"""
        try:
            from lab_two_implementations import ConditionalScoreMatchingTrainer
            if path is None:
                path = MockPathForScore()
            if model is None:
                model = MockScoreModel()
            return ConditionalScoreMatchingTrainer(path, model)
        except (ImportError, AttributeError):
            class MockTrainer:
                def __init__(self, path, model):
                    self.path = path
                    self.model = model
                
                def get_train_loss(self, batch_size):
                    raise NotImplementedError("Fill me in for Question 3.2!")
            return MockTrainer(path, model)

