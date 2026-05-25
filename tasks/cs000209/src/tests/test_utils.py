"""Tests for utility functions."""

import os
import tempfile
import pytest
from utils import save_run
from config import Config
from tree import Journal
from nodes import Node


def test_save_run():
    """Test saving best solution and good solutions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        # Create config
        config_dict = {
            "exp_name": "test",
            "data_dir": "/path/to/data"
        }
        cfg = Config(config_dict)
        
        # Create journal with nodes
        journal = Journal()
        node1 = Node(code="print('solution1')", is_buggy=False, metric=0.5)
        node2 = Node(code="print('solution2')", is_buggy=False, metric=0.3)
        node3 = Node(code="print('buggy')", is_buggy=True, metric=1.0)
        
        journal.append(node1)
        journal.append(node2)
        journal.append(node3)
        
        # Save run
        save_run(cfg, journal)
        
        # Check that files were created
        assert os.path.exists("best_solution.py")
        assert os.path.exists("good_solution_0.py")
        assert os.path.exists("good_solution_1.py")
        
        # Check file contents
        with open("best_solution.py", "r") as f:
            best_code = f.read()
            # Best node should be node2 (lowest metric)
            assert "solution2" in best_code
        
        with open("good_solution_0.py", "r") as f:
            good_code = f.read()
            assert "solution" in good_code


def test_save_run_no_nodes():
    """Test saving when journal is empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        
        config_dict = {"exp_name": "test"}
        cfg = Config(config_dict)
        journal = Journal()
        
        # Should not raise error
        save_run(cfg, journal)

