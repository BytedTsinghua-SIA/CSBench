"""
Unit tests for image classification dataset module.
"""

import unittest
from unittest.mock import Mock
import torch
from pathlib import Path
import tempfile
import shutil
from PIL import Image

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_classification.dataset import CustomImageDataset, get_data_loaders


class TestCustomImageDataset(unittest.TestCase):
    """Test CustomImageDataset class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.categories = ['cat', 'dog']
        
        for category in self.categories:
            category_dir = Path(self.temp_dir) / category
            category_dir.mkdir(parents=True)
            for i in range(5):
                img = Image.new('RGB', (100, 100), color=(i*50, i*50, i*50))
                img.save(category_dir / f'img_{i}.png')
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_dataset_initialization(self):
        """Test dataset initialization."""
        transform = Mock()
        dataset = CustomImageDataset(self.temp_dir, transform=transform, categories=self.categories)
        self.assertEqual(len(dataset), 10)
        self.assertEqual(dataset.get_num_classes(), 2)


class TestGetDataLoaders(unittest.TestCase):
    """Test get_data_loaders function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        for split in ['train', 'val', 'test']:
            split_dir = Path(self.temp_dir) / split
            split_dir.mkdir(parents=True)
            for category in ['cat', 'dog']:
                category_dir = split_dir / category
                category_dir.mkdir(parents=True)
                for i in range(3):
                    img = Image.new('RGB', (100, 100), color=(i*50, i*50, i*50))
                    img.save(category_dir / f'img_{i}.png')
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_data_loaders_returns_three_loaders(self):
        """Test get_data_loaders returns train, val, and test loaders."""
        train_loader, val_loader, test_loader = get_data_loaders(
            self.temp_dir, batch_size=2, num_workers=0
        )
        self.assertIsNotNone(train_loader)
        self.assertIsNotNone(val_loader)
        self.assertIsNotNone(test_loader)


if __name__ == '__main__':
    unittest.main()
