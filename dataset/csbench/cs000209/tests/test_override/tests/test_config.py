"""Tests for Config class."""

import pytest
from config import Config, set_seed


def test_config_creation():
    """Test Config creation from dictionary."""
    config_dict = {
        "exp_name": "test",
        "data_dir": "/path/to/data",
        "agent": {
            "steps": 10,
            "search": {
                "debug_prob": 0.5,
                "num_drafts": 3
            }
        }
    }
    
    cfg = Config(config_dict)
    assert cfg.exp_name == "test"
    assert cfg.data_dir == "/path/to/data"
    assert cfg.agent.steps == 10
    assert cfg.agent.search.debug_prob == 0.5
    assert cfg.agent.search.num_drafts == 3


def test_config_nested():
    """Test nested Config objects."""
    config_dict = {
        "level1": {
            "level2": {
                "value": 42
            }
        }
    }
    
    cfg = Config(config_dict)
    assert isinstance(cfg.level1, Config)
    assert isinstance(cfg.level1.level2, Config)
    assert cfg.level1.level2.value == 42


def test_set_seed():
    """Test seed setting function."""
    # This should not raise an error
    set_seed(42)
    set_seed()  # Default seed

