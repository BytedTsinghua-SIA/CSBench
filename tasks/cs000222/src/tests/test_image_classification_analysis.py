"""
Unit tests for image classification analysis module.
"""

import unittest
from unittest.mock import Mock
import torch
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_classification.analysis import compute_confusion_matrix, compute_saliency_map


class TestComputeConfusionMatrix(unittest.TestCase):
    """Test compute_confusion_matrix function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.device = torch.device('cpu')
        self.class_names = ['cat', 'dog']
        self.model = torch.nn.Sequential(torch.nn.Linear(10, 2))
        self.mock_dataloader = Mock()
        self.mock_dataloader.__iter__ = Mock(return_value=iter([
            (torch.randn(2, 10), torch.tensor([0, 1]))
        ]))
    
    def test_compute_confusion_matrix_returns_array(self):
        """Test compute_confusion_matrix returns numpy array."""
        cm = compute_confusion_matrix(
            self.model, self.mock_dataloader, self.device, self.class_names
        )
        self.assertIsInstance(cm, np.ndarray)
        self.assertEqual(cm.shape, (2, 2))


class TestComputeSaliencyMap(unittest.TestCase):
    """Test compute_saliency_map function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.device = torch.device('cpu')
        # Use a model that can handle image input (flatten first)
        self.model = torch.nn.Sequential(
            torch.nn.Flatten(),
            torch.nn.Linear(3 * 32 * 32, 2)
        )
        self.image = torch.randn(1, 3, 32, 32, requires_grad=True)
    
    def test_compute_saliency_map_returns_array(self):
        """Test compute_saliency_map returns numpy array."""
        saliency = compute_saliency_map(self.model, self.image, device=self.device)
        self.assertIsInstance(saliency, np.ndarray)
        self.assertEqual(len(saliency.shape), 2)


if __name__ == '__main__':
    unittest.main()
