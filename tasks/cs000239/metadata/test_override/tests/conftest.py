"""
Pytest configuration for CS285 Homework 1 tests
"""
import pytest
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def setup_pytorch():
    """Setup PyTorch for each test"""
    from cs285.infrastructure import pytorch_util as ptu
    ptu.init_gpu(use_gpu=False)
    yield
    # Cleanup if needed