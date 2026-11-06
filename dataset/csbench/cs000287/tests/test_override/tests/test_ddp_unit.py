"""
Unit tests for ddp.py module.
"""

import pytest
import torch
import torch.nn as nn
import torch.distributed as dist
from unittest.mock import Mock, patch, MagicMock

from cs336_systems.ddp import DDPIndividualParameters, DDPBucketed


class SimpleModel(nn.Module):
    """Simple model for testing."""
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 5)
    
    def forward(self, x):
        return self.linear(x)


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
def test_ddp_individual_parameters_init(mock_broadcast, mock_rank, mock_world_size):
    """Test DDPIndividualParameters initialization."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    ddp_model = DDPIndividualParameters(model)
    
    assert ddp_model.module == model
    assert ddp_model.world_size == 2
    assert ddp_model.rank == 0
    assert len(ddp_model._pending_grad_syncs) == 0
    assert mock_broadcast.call_count > 0


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
def test_ddp_individual_parameters_forward(mock_broadcast, mock_rank, mock_world_size):
    """Test DDPIndividualParameters forward pass."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    ddp_model = DDPIndividualParameters(model)
    
    x = torch.randn(4, 10)
    output = ddp_model(x)
    
    expected_output = model(x)
    torch.testing.assert_close(output, expected_output)


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
@patch("cs336_systems.ddp.dist.all_reduce")
def test_ddp_individual_parameters_grad_hook(mock_all_reduce, mock_broadcast, mock_rank, mock_world_size):
    """Test DDPIndividualParameters gradient hook registration."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    mock_handle = MagicMock()
    mock_all_reduce.return_value = mock_handle
    
    model = SimpleModel()
    ddp_model = DDPIndividualParameters(model)
    
    x = torch.randn(4, 10)
    output = ddp_model(x)
    loss = output.sum()
    loss.backward()
    
    assert len(ddp_model._pending_grad_syncs) > 0


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
def test_ddp_individual_parameters_finish_sync(mock_broadcast, mock_rank, mock_world_size):
    """Test DDPIndividualParameters finish gradient synchronization."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    mock_handle = MagicMock()
    
    model = SimpleModel()
    ddp_model = DDPIndividualParameters(model)
    ddp_model._pending_grad_syncs = [mock_handle]
    
    ddp_model.finish_gradient_synchronization()
    
    mock_handle.wait.assert_called_once()
    assert len(ddp_model._pending_grad_syncs) == 0


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
def test_ddp_bucketed_init(mock_broadcast, mock_rank, mock_world_size):
    """Test DDPBucketed initialization."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    ddp_model = DDPBucketed(model, bucket_size_mb=0.1)
    
    assert ddp_model.module == model
    assert ddp_model.world_size == 2
    assert ddp_model.rank == 0
    assert ddp_model.bucket_size_mb == 0.1
    assert len(ddp_model._buckets) > 0
    assert mock_broadcast.call_count > 0


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
def test_ddp_bucketed_forward(mock_broadcast, mock_rank, mock_world_size):
    """Test DDPBucketed forward pass."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    ddp_model = DDPBucketed(model, bucket_size_mb=0.1)
    
    x = torch.randn(4, 10)
    output = ddp_model(x)
    
    expected_output = model(x)
    torch.testing.assert_close(output, expected_output)


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
def test_ddp_bucketed_create_buckets(mock_broadcast, mock_rank, mock_world_size):
    """Test DDPBucketed bucket creation."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    ddp_model = DDPBucketed(model, bucket_size_mb=0.001)
    
    buckets = ddp_model._buckets
    assert len(buckets) > 0
    
    all_params = list(model.parameters())
    params_in_buckets = []
    for bucket in buckets:
        params_in_buckets.extend(bucket)
    
    assert len(params_in_buckets) == len(all_params)


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
@patch("cs336_systems.ddp.dist.all_reduce")
def test_ddp_bucketed_finish_sync(mock_all_reduce, mock_broadcast, mock_rank, mock_world_size):
    """Test DDPBucketed finish gradient synchronization."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    mock_handle = MagicMock()
    mock_all_reduce.return_value = mock_handle
    
    model = SimpleModel()
    ddp_model = DDPBucketed(model, bucket_size_mb=0.1)
    
    # Simulate gradients being computed by manually adding them to _bucket_grads
    # This simulates what would happen during a backward pass
    if len(ddp_model._buckets) > 0:
        bucket_idx = 0
        ddp_model._bucket_grads[bucket_idx] = {}
        for param_idx, param in enumerate(ddp_model._buckets[bucket_idx]):
            if param.requires_grad:
                ddp_model._bucket_grads[bucket_idx][param_idx] = torch.randn_like(param)
    
    ddp_model.finish_gradient_synchronization()
    
    # If we had gradients, handle.wait should have been called
    if mock_all_reduce.called:
        mock_handle.wait.assert_called()


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
def test_ddp_bucketed_large_bucket_size(mock_broadcast, mock_rank, mock_world_size):
    """Test DDPBucketed with large bucket size."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    ddp_model = DDPBucketed(model, bucket_size_mb=100.0)
    
    buckets = ddp_model._buckets
    assert len(buckets) >= 1


@patch("cs336_systems.ddp.dist.get_world_size")
@patch("cs336_systems.ddp.dist.get_rank")
@patch("cs336_systems.ddp.dist.broadcast")
def test_ddp_bucketed_small_bucket_size(mock_broadcast, mock_rank, mock_world_size):
    """Test DDPBucketed with small bucket size."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    ddp_model = DDPBucketed(model, bucket_size_mb=0.0001)
    
    buckets = ddp_model._buckets
    assert len(buckets) > 0

