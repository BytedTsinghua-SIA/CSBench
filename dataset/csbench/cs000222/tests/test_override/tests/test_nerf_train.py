"""
Unit tests for NeRF training module.
"""

import unittest
from unittest.mock import Mock
import torch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nerf.train import NeRFTrainer
from nerf.models import NeRF


class TestNeRFTrainer(unittest.TestCase):
    """Test NeRFTrainer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.device = torch.device('cpu')
        self.model = NeRF(num_layers=4, hidden_dim=64)
        self.mock_train_loader = Mock()
        self.mock_train_loader.__iter__ = Mock(return_value=iter([
            {'image': torch.rand(32, 32, 3), 'pose': torch.eye(4), 'focal': 50.0}
        ]))
        self.mock_val_loader = None
    
    def test_trainer_initialization(self):
        """Test NeRFTrainer initialization."""
        trainer = NeRFTrainer(
            self.model, self.mock_train_loader, self.mock_val_loader,
            self.device
        )
        self.assertIsNotNone(trainer.model)
        self.assertIsNotNone(trainer.optimizer)


if __name__ == '__main__':
    unittest.main()
