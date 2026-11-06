import torch
import torch.distributed as dist
import os
import pytest

def test_pytorch_basic():
    """Verify basic PyTorch tensor operations on CPU."""
    x = torch.ones(5, 3)
    y = torch.zeros(5, 3)
    z = x + y
    assert z.shape == (5, 3)
    assert torch.all(z == 1.0)

def test_distributed_backend_init():
    """Verify that the gloo backend can be initialized on CPU."""
    # Set environment variables for local initialization
    os.environ['MASTER_ADDR'] = '127.0.0.1'
    os.environ['MASTER_PORT'] = '29500'
    
    try:
        # Initialize with world_size=1 for a quick check
        dist.init_process_group(backend='gloo', rank=0, world_size=1)
        assert dist.is_initialized()
        assert dist.get_backend() == 'gloo'
    finally:
        if dist.is_initialized():
            dist.destroy_process_group()

def test_available_cpus():
    """Verify that we are running in a multicore-aware environment."""
    import multiprocessing
    cpu_count = multiprocessing.cpu_count()
    assert cpu_count >= 1
