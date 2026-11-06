"""
Test PyTorch utilities for CS285 Homework 2
"""
import torch
import numpy as np
import pytest

from cs285.infrastructure import pytorch_util as ptu


class TestPyTorchUtil:
    """Test PyTorch utility functions"""

    def setup_method(self):
        """Setup before each test"""
        ptu.init_gpu(use_gpu=False)

    def test_init_gpu_cpu(self):
        """Test GPU initialization with CPU fallback"""
        assert ptu.device.type == 'cpu'

    def test_build_mlp_basic(self):
        """Test basic MLP construction"""
        input_size = 10
        output_size = 5
        n_layers = 2
        size = 32

        mlp = ptu.build_mlp(
            input_size=input_size,
            output_size=output_size,
            n_layers=n_layers,
            size=size,
            activation='relu',
            output_activation='identity'
        )

        assert isinstance(mlp, torch.nn.Module)
        assert isinstance(mlp, torch.nn.Sequential)

        # Count layers: n_layers hidden layers + output layer
        total_modules = (n_layers * 2) + 2  # Input layer + hidden layers + output
        assert len(mlp) == total_modules

        # Test forward pass
        batch_size = 4
        x = torch.randn(batch_size, input_size)
        output = mlp(x)

        assert output.shape == (batch_size, output_size)

    def test_build_mlp_different_activations(self):
        """Test MLP construction with different activation functions"""
        mlp = ptu.build_mlp(
            input_size=8,
            output_size=3,
            n_layers=1,
            size=16,
            activation='tanh',
            output_activation='sigmoid'
        )

        # Check activation types
        assert isinstance(mlp[1], torch.nn.Tanh)  # Hidden activation
        assert isinstance(mlp[3], torch.nn.Sigmoid)  # Output activation

    def test_build_mlp_no_hidden_layers(self):
        """Test MLP with no hidden layers (n_layers=0)"""
        mlp = ptu.build_mlp(
            input_size=6,
            output_size=2,
            n_layers=0,  # No hidden layers
            size=32,  # Size parameter ignored when n_layers=0
            activation='relu',
            output_activation='identity'
        )

        # Should have input layer and output layer only
        assert len(mlp) == 2  # Linear + OutputActivation
        assert isinstance(mlp[0], torch.nn.Linear)
        assert mlp[0].in_features == 6
        assert mlp[0].out_features == 2

    def test_from_numpy(self):
        """Test conversion from numpy to torch tensor"""
        arr = np.random.randn(3, 4).astype(np.float32)
        tensor = ptu.from_numpy(arr)

        assert isinstance(tensor, torch.Tensor)
        assert tensor.shape == (3, 4)
        assert tensor.dtype == torch.float32
        assert tensor.device.type == 'cpu'

    def test_to_numpy(self):
        """Test conversion from torch tensor to numpy"""
        tensor = torch.randn(2, 3, dtype=torch.float32)
        arr = ptu.to_numpy(tensor)

        assert isinstance(arr, np.ndarray)
        assert arr.shape == (2, 3)
        assert arr.dtype == np.float32

    def test_device_consistency(self):
        """Test that device is consistent across utility functions"""
        # Force CPU mode
        ptu.init_gpu(use_gpu=False)

        # Create tensor using from_numpy
        arr = np.random.randn(3, 2).astype(np.float32)
        tensor = ptu.from_numpy(arr)

        assert tensor.device.type == 'cpu'

        # Convert back
        arr_back = ptu.to_numpy(tensor)
        assert isinstance(arr_back, np.ndarray)

    def test_mlp_gradient_flow(self):
        """Test that gradients flow through MLP"""
        mlp = ptu.build_mlp(
            input_size=4,
            output_size=2,
            n_layers=1,
            size=8,
            activation='relu'
        )

        # Enable training mode
        mlp.train()

        # Create input with requires_grad
        x = torch.randn(2, 4, requires_grad=True)
        output = mlp(x)

        # Compute loss and backward
        target = torch.randn(2, 2)
        loss = torch.nn.functional.mse_loss(output, target)
        loss.backward()

        # Check gradients
        assert x.grad is not None
        assert x.grad.shape == x.shape

        # Check that MLP parameters have gradients
        for param in mlp.parameters():
            assert param.grad is not None
            assert not torch.all(param.grad == 0)  # Gradients should be non-zero
