"""
Unit tests for CFGTrainer
"""
import pytest
import torch
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab_three import (
    CFGTrainer,
    GaussianConditionalProbabilityPath,
    ConditionalVectorField,
    Sampleable,
    LinearAlpha,
    LinearBeta
)


class MockDataSampler(Sampleable):
    """Mock data sampler for testing"""
    def __init__(self, shape):
        self.shape = shape
    
    def sample(self, num_samples):
        z = torch.randn(num_samples, *self.shape)
        y = torch.randint(0, 10, (num_samples,))
        return z, y


class MockVectorField(ConditionalVectorField):
    """Mock vector field for testing"""
    def __init__(self):
        super().__init__()
        # Add a parameter to ensure gradients flow
        self.weight = torch.nn.Parameter(torch.ones(1))
    
    def forward(self, x, t, y):
        # Use a parameter-based operation to ensure requires_grad
        return self.weight * torch.randn_like(x) + 0.1 * x


class TestCFGTrainer:
    """Test cases for CFGTrainer"""
    
    def test_initialization(self):
        """Test CFGTrainer initialization with valid and invalid eta"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        model = MockVectorField()
        
        # Valid eta
        trainer = CFGTrainer(path=path, model=model, eta=0.1)
        assert trainer.eta == 0.1
        assert trainer.path == path
        assert trainer.model == model
        
        # Invalid eta values
        with pytest.raises(AssertionError):
            CFGTrainer(path=path, model=model, eta=0.0)
        with pytest.raises(AssertionError):
            CFGTrainer(path=path, model=model, eta=1.0)
        
        # Edge cases: eta very close to boundaries
        trainer_edge1 = CFGTrainer(path=path, model=model, eta=0.001)
        assert trainer_edge1.eta == 0.001
        trainer_edge2 = CFGTrainer(path=path, model=model, eta=0.999)
        assert trainer_edge2.eta == 0.999
    
    def test_get_train_loss_output_shape(self):
        """Test that get_train_loss returns scalar tensor with correct properties"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        model = MockVectorField()
        trainer = CFGTrainer(path=path, model=model, eta=0.1)
        
        # Test with different batch sizes including edge case
        for batch_size in [1, 4, 8]:
            loss = trainer.get_train_loss(batch_size=batch_size)
            assert isinstance(loss, torch.Tensor)
            assert loss.shape == ()
            assert loss.requires_grad
            assert loss.item() >= 0  # Loss should be non-negative
        
        # Edge case: very small batch size
        loss = trainer.get_train_loss(batch_size=1)
        assert loss.shape == () and loss.item() >= 0
    
    def test_get_train_loss_label_replacement(self):
        """Test that labels are replaced with null label (10) with probability eta"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        # Track calls to model.forward to check labels
        call_labels = []
        def track_forward(x, t, y):
            call_labels.append(y.clone())
            return torch.randn_like(x)
        
        # Use a proper mock class instead of Mock()
        class TrackedModel(ConditionalVectorField):
            def forward(self, x, t, y):
                call_labels.append(y.clone())
                return torch.randn_like(x)
        
        model = TrackedModel()
        
        trainer = CFGTrainer(path=path, model=model, eta=0.5)
        
        # Run multiple times to check label replacement
        for _ in range(10):
            trainer.get_train_loss(batch_size=10)
        
        # Check that some labels are 10 (null label)
        all_labels = torch.cat(call_labels)
        assert torch.any(all_labels == 10)
    
    def test_get_train_loss_uses_correct_shapes_and_sampling(self):
        """Test that get_train_loss uses correct shapes and samples correctly"""
        p_data = MockDataSampler([1, 32, 32])
        path = GaussianConditionalProbabilityPath(
            p_data=p_data,
            p_simple_shape=[1, 32, 32],
            alpha=LinearAlpha(),
            beta=LinearBeta()
        )
        
        call_args = []
        sampled_t_values = []
        
        class TrackedModel(ConditionalVectorField):
            def forward(self, x, t, y):
                call_args.append((x.shape, t.shape, y.shape))
                sampled_t_values.append(t.clone())
                return torch.randn_like(x)
        
        model = TrackedModel()
        
        trainer = CFGTrainer(path=path, model=model, eta=0.1)
        trainer.get_train_loss(batch_size=5)
        
        # Check shapes
        assert len(call_args) > 0
        x_shape, t_shape, y_shape = call_args[0]
        assert x_shape == (5, 1, 32, 32)
        assert t_shape == (5, 1, 1, 1)
        assert y_shape == (5,)
        
        # Check t is sampled from [0, 1]
        all_t = torch.cat(sampled_t_values)
        assert torch.all(all_t >= 0.0) and torch.all(all_t <= 1.0)

