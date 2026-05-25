"""
Unit tests for super-resolution training module.
"""

import unittest
from unittest.mock import Mock
import torch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from super_resolution.train import SuperResolutionTrainer
from super_resolution.models import SRCNN


class TestSuperResolutionTrainer(unittest.TestCase):
    """Test SuperResolutionTrainer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.device = torch.device('cpu')
        self.model = SRCNN(scale_factor=2)
        self.mock_train_loader = Mock()
        self.mock_train_loader.__iter__ = Mock(return_value=iter([
            {'y_lr': torch.randn(2, 1, 16, 16), 'y_hr': torch.randn(2, 1, 32, 32)}
        ]))
        self.mock_val_loader = None
    
    def test_trainer_initialization(self):
        """Test SuperResolutionTrainer initialization."""
        trainer = SuperResolutionTrainer(
            self.model, self.mock_train_loader, self.mock_val_loader,
            self.device
        )
        self.assertIsNotNone(trainer.model)
        self.assertIsNotNone(trainer.optimizer)


if __name__ == '__main__':
    unittest.main()
