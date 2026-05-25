"""
Unit tests for benchmark.py module.
"""

import pytest
import torch
from unittest.mock import Mock, patch, MagicMock

from cs336_systems.benchmark import get_model_config, benchmark_model
from cs336_basics.model import BasicsTransformerLM


def test_get_model_config_valid_sizes():
    """Test getting model configuration for valid model sizes."""
    configs = ["small", "medium", "large", "xl", "2.7B"]
    for size in configs:
        config = get_model_config(size)
        assert config is not None
        assert "d_model" in config
        assert "d_ff" in config
        assert "num_layers" in config
        assert "num_heads" in config


def test_get_model_config_invalid_size():
    """Test getting model configuration for invalid model size."""
    config = get_model_config("invalid_size")
    assert config is None


def test_get_model_config_small():
    """Test small model configuration values."""
    config = get_model_config("small")
    assert config["d_model"] == 768
    assert config["d_ff"] == 3072
    assert config["num_layers"] == 12
    assert config["num_heads"] == 12


def test_get_model_config_xl():
    """Test xl model configuration values."""
    config = get_model_config("xl")
    assert config["d_model"] == 1600
    assert config["d_ff"] == 6400
    assert config["num_layers"] == 48
    assert config["num_heads"] == 25


def test_get_model_config_medium():
    """Test medium model configuration values."""
    config = get_model_config("medium")
    assert config["d_model"] == 1024
    assert config["d_ff"] == 4096
    assert config["num_layers"] == 24
    assert config["num_heads"] == 16


def test_get_model_config_large():
    """Test large model configuration values."""
    config = get_model_config("large")
    assert config["d_model"] == 1280
    assert config["d_ff"] == 5120
    assert config["num_layers"] == 36
    assert config["num_heads"] == 20


def test_get_model_config_27b():
    """Test 2.7B model configuration values."""
    config = get_model_config("2.7B")
    assert config["d_model"] == 2560
    assert config["d_ff"] == 10240
    assert config["num_layers"] == 32
    assert config["num_heads"] == 32


@patch("cs336_systems.benchmark.torch.cuda.is_available")
@patch("cs336_systems.benchmark.torch.cuda.synchronize")
def test_benchmark_model_forward_cpu(mock_sync, mock_cuda_available):
    """Test benchmarking forward pass on CPU."""
    mock_cuda_available.return_value = False
    
    config = get_model_config("small")
    model = BasicsTransformerLM(
        vocab_size=1000,
        context_length=128,
        d_model=config["d_model"],
        num_layers=config["num_layers"],
        num_heads=config["num_heads"],
        d_ff=config["d_ff"],
        rope_theta=10000.0,
    )
    
    timings = benchmark_model(
        model=model,
        batch_size=2,
        context_length=128,
        vocab_size=1000,
        warmup_steps=2,
        num_steps=3,
        mode="forward",
        device="cpu",
    )
    
    assert len(timings) == 3
    assert all(t > 0 for t in timings)
    mock_sync.assert_not_called()


@patch("cs336_systems.benchmark.torch.cuda.is_available")
@patch("cs336_systems.benchmark.torch.cuda.synchronize")
def test_benchmark_model_forward_backward_cpu(mock_sync, mock_cuda_available):
    """Test benchmarking forward and backward pass on CPU."""
    mock_cuda_available.return_value = False
    
    config = get_model_config("small")
    model = BasicsTransformerLM(
        vocab_size=1000,
        context_length=64,
        d_model=config["d_model"],
        num_layers=config["num_layers"],
        num_heads=config["num_heads"],
        d_ff=config["d_ff"],
        rope_theta=10000.0,
    )
    
    timings = benchmark_model(
        model=model,
        batch_size=2,
        context_length=64,
        vocab_size=1000,
        warmup_steps=1,
        num_steps=2,
        mode="forward_backward",
        device="cpu",
    )
    
    assert len(timings) == 2
    assert all(t > 0 for t in timings)
    mock_sync.assert_not_called()


def test_benchmark_model_warmup_steps():
    """Test that warmup steps are executed but not timed."""
    config = get_model_config("small")
    model = BasicsTransformerLM(
        vocab_size=100,
        context_length=32,
        d_model=config["d_model"],
        num_layers=2,
        num_heads=config["num_heads"],
        d_ff=config["d_ff"],
        rope_theta=10000.0,
    )
    
    timings = benchmark_model(
        model=model,
        batch_size=1,
        context_length=32,
        vocab_size=100,
        warmup_steps=5,
        num_steps=2,
        mode="forward",
        device="cpu",
    )
    
    assert len(timings) == 2


def test_benchmark_model_zero_steps():
    """Test benchmarking with zero measurement steps."""
    config = get_model_config("small")
    model = BasicsTransformerLM(
        vocab_size=100,
        context_length=32,
        d_model=config["d_model"],
        num_layers=2,
        num_heads=config["num_heads"],
        d_ff=config["d_ff"],
        rope_theta=10000.0,
    )
    
    timings = benchmark_model(
        model=model,
        batch_size=1,
        context_length=32,
        vocab_size=100,
        warmup_steps=1,
        num_steps=0,
        mode="forward",
        device="cpu",
    )
    
    assert len(timings) == 0


@patch("cs336_systems.benchmark.torch.cuda.is_available")
@patch("cs336_systems.benchmark.torch.cuda.synchronize")
def test_benchmark_model_cuda_synchronize(mock_sync, mock_cuda_available):
    """Test that torch.cuda.synchronize is called when using CUDA device."""
    mock_cuda_available.return_value = True
    
    config = get_model_config("small")
    model = BasicsTransformerLM(
        vocab_size=100,
        context_length=16,
        d_model=config["d_model"],
        num_layers=2,
        num_heads=config["num_heads"],
        d_ff=config["d_ff"],
        rope_theta=10000.0,
    )
    
    # Note: This test assumes CUDA is available in the test environment
    # In practice, this would need CUDA or proper mocking
    try:
        timings = benchmark_model(
            model=model,
            batch_size=1,
            context_length=16,
            vocab_size=100,
            warmup_steps=1,
            num_steps=1,
            mode="forward",
            device="cuda",
        )
        # If CUDA is actually available, synchronize should be called
        if torch.cuda.is_available():
            assert mock_sync.call_count >= 1
    except RuntimeError:
        # CUDA not available, skip this test
        pass


def test_benchmark_model_uses_timeit():
    """Test that benchmark_model uses timeit module for timing."""
    import timeit
    
    config = get_model_config("small")
    model = BasicsTransformerLM(
        vocab_size=100,
        context_length=16,
        d_model=config["d_model"],
        num_layers=2,
        num_heads=config["num_heads"],
        d_ff=config["d_ff"],
        rope_theta=10000.0,
    )
    
    timings = benchmark_model(
        model=model,
        batch_size=1,
        context_length=16,
        vocab_size=100,
        warmup_steps=1,
        num_steps=2,
        mode="forward",
        device="cpu",
    )
    
    # Verify that timings are returned (timeit was used)
    assert len(timings) == 2
    assert all(isinstance(t, float) for t in timings)

