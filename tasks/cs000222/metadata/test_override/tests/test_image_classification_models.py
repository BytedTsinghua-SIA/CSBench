"""
Unit tests for image classification models module.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import torch
import torch.nn as nn

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_classification.models import get_model, LinearClassifier


class TestGetModel(unittest.TestCase):
    """Test get_model function."""
    
    @patch('image_classification.models.models.resnet18')
    def test_get_model_creates_model(self, mock_resnet):
        """Test get_model creates model."""
        mock_model = MagicMock()
        mock_model.fc = MagicMock()
        mock_model.fc.in_features = 512
        mock_resnet.return_value = mock_model
        
        model = get_model('resnet18', num_classes=10, pretrained=False)
        self.assertIsNotNone(model)
    
    def test_get_model_unknown_model(self):
        """Test get_model raises error for unknown model."""
        with self.assertRaises(ValueError):
            get_model('unknown_model', num_classes=10)


class TestLinearClassifier(unittest.TestCase):
    """Test LinearClassifier class."""
    
    def test_linear_classifier_initialization(self):
        """Test LinearClassifier initialization."""
        classifier = LinearClassifier(input_dim=512, num_classes=10)
        self.assertIsInstance(classifier.fc, nn.Linear)
        self.assertEqual(classifier.fc.out_features, 10)


if __name__ == '__main__':
    unittest.main()
