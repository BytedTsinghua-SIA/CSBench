"""
Pytest configuration and shared fixtures.
"""

import pytest
import torch
import numpy as np


@pytest.fixture
def device():
    """Fixture for PyTorch device."""
    return torch.device('cpu')


@pytest.fixture
def seed():
    """Fixture to set random seed for reproducibility."""
    torch.manual_seed(42)
    np.random.seed(42)
    return 42

