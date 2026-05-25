"""
Unit tests for sharded_optimizer.py module.
"""

import pytest
import torch
import torch.nn as nn
import torch.distributed as dist
from unittest.mock import Mock, patch, MagicMock

from cs336_systems.sharded_optimizer import ShardedOptimizer


class SimpleModel(nn.Module):
    """Simple model for testing."""
    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(10, 5)
        self.linear2 = nn.Linear(5, 3)
    
    def forward(self, x):
        x = self.linear1(x)
        x = self.linear2(x)
        return x


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
def test_sharded_optimizer_init(mock_rank, mock_world_size):
    """Test ShardedOptimizer initialization."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    optimizer = ShardedOptimizer(model.parameters(), torch.optim.SGD, lr=0.01)
    
    assert optimizer.world_size == 2
    assert optimizer.rank == 0
    assert len(optimizer._all_params) > 0
    assert optimizer.base_optimizer is not None


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
def test_sharded_optimizer_parameter_sharding(mock_rank, mock_world_size):
    """Test that parameters are correctly sharded across ranks."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    params = list(model.parameters())
    
    optimizer = ShardedOptimizer(params, torch.optim.SGD, lr=0.01)
    
    assert len(optimizer._local_params) <= len(params)
    # Use id() comparison since tensor 'in' operator does value comparison
    all_param_ids = {id(p) for p in optimizer._all_params}
    assert all(id(p) in all_param_ids for p in params)
    assert all(optimizer._param_to_rank[p] == 0 or optimizer._param_to_rank[p] == 1 for p in params)


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
@patch("cs336_systems.sharded_optimizer.dist.broadcast")
def test_sharded_optimizer_step(mock_broadcast, mock_rank, mock_world_size):
    """Test ShardedOptimizer step method."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    optimizer = ShardedOptimizer(model.parameters(), torch.optim.SGD, lr=0.01)
    
    x = torch.randn(4, 10)
    output = model(x)
    loss = output.sum()
    loss.backward()
    
    optimizer.step()
    
    assert mock_broadcast.call_count > 0


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
def test_sharded_optimizer_zero_grad(mock_rank, mock_world_size):
    """Test ShardedOptimizer zero_grad method."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    optimizer = ShardedOptimizer(model.parameters(), torch.optim.SGD, lr=0.01)
    
    x = torch.randn(4, 10)
    output = model(x)
    loss = output.sum()
    loss.backward()
    
    optimizer.zero_grad()
    
    for param in model.parameters():
        if param.grad is not None:
            assert param.grad.sum() == 0


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
def test_sharded_optimizer_add_param_group(mock_rank, mock_world_size):
    """Test ShardedOptimizer add_param_group method."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    optimizer = ShardedOptimizer(model.parameters(), torch.optim.SGD, lr=0.01)
    
    new_param = nn.Parameter(torch.randn(3, 2))
    initial_param_count = len(optimizer._all_params)
    
    optimizer.add_param_group({"params": [new_param], "lr": 0.02})
    
    assert len(optimizer._all_params) == initial_param_count + 1
    # Use id() comparison since tensor 'in' operator does value comparison
    assert any(new_param is p for p in optimizer._all_params)


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
def test_sharded_optimizer_empty_params(mock_rank, mock_world_size):
    """Test ShardedOptimizer with empty parameter list."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    with pytest.raises(ValueError, match="empty parameter list"):
        ShardedOptimizer([], torch.optim.SGD, lr=0.01)


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
@patch("cs336_systems.sharded_optimizer.dist.broadcast")
def test_sharded_optimizer_synchronize_parameters(mock_broadcast, mock_rank, mock_world_size):
    """Test parameter synchronization after step."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 1
    
    model = SimpleModel()
    optimizer = ShardedOptimizer(model.parameters(), torch.optim.SGD, lr=0.01)
    
    optimizer._synchronize_parameters()
    
    assert mock_broadcast.call_count > 0


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
def test_sharded_optimizer_rank_assignment(mock_rank, mock_world_size):
    """Test that parameters are assigned to correct ranks."""
    mock_world_size.return_value = 3
    mock_rank.return_value = 1
    
    model = SimpleModel()
    params = list(model.parameters())
    
    optimizer = ShardedOptimizer(params, torch.optim.SGD, lr=0.01)
    
    for idx, param in enumerate(params):
        expected_rank = idx % 3
        assert optimizer._param_to_rank[param] == expected_rank


@patch("cs336_systems.sharded_optimizer.dist.get_world_size")
@patch("cs336_systems.sharded_optimizer.dist.get_rank")
def test_sharded_optimizer_state_dict(mock_rank, mock_world_size):
    """Test ShardedOptimizer state_dict method."""
    mock_world_size.return_value = 2
    mock_rank.return_value = 0
    
    model = SimpleModel()
    optimizer = ShardedOptimizer(model.parameters(), torch.optim.SGD, lr=0.01)
    
    state = optimizer.state_dict()
    assert "state" in state or "param_groups" in state

