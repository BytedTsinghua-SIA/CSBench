"""
Unit tests for image classification training module.
"""

import unittest
from unittest.mock import Mock
import torch
import torch.nn as nn
import torch.optim as optim

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_classification.train import Trainer


class TestTrainer(unittest.TestCase):
    """Test Trainer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.device = torch.device('cpu')
        self.model = nn.Linear(10, 2)
        self.mock_train_loader = Mock()
        self.mock_train_loader.__iter__ = Mock(return_value=iter([
            (torch.randn(2, 10), torch.tensor([0, 1]))
        ]))
        self.mock_val_loader = Mock()
        self.mock_val_loader.__iter__ = Mock(return_value=iter([
            (torch.randn(2, 10), torch.tensor([1, 0]))
        ]))
    
    def test_trainer_initialization(self):
        """Test Trainer initialization."""
        trainer = Trainer(
            self.model, self.mock_train_loader, self.mock_val_loader,
            self.device, optimizer_name='adam'
        )
        self.assertIsNotNone(trainer.model)
        self.assertIsNotNone(trainer.optimizer)


if __name__ == '__main__':
    unittest.main()
