"""
Unit tests for MNISTSampler
"""
import pytest
import torch
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import lab_three
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab_three import MNISTSampler, Sampleable


class TestMNISTSampler:
    """Test cases for MNISTSampler class"""
    
    @patch('lab_three.datasets.MNIST')
    def test_mnist_sampler_initialization(self, mock_mnist_dataset):
        """Test MNISTSampler initialization"""
        mock_dataset = MagicMock()
        mock_mnist_dataset.return_value = mock_dataset
        
        sampler = MNISTSampler()
        
        assert sampler.dataset is not None
        mock_mnist_dataset.assert_called_once()
    
    @patch('lab_three.datasets.MNIST')
    def test_sample_valid_num_samples(self, mock_mnist_dataset):
        """Test sampling with valid number of samples"""
        # Setup mock dataset
        mock_dataset = MagicMock()
        mock_dataset.__len__ = lambda x: 100
        
        # Create enough sample data for any possible index
        mock_samples = [torch.randn(1, 32, 32) for _ in range(100)]
        mock_labels = [i % 10 for i in range(100)]
        
        def get_item(self, idx):
            # Handle any index by using modulo
            actual_idx = idx % len(mock_samples)
            return (mock_samples[actual_idx], mock_labels[actual_idx])
        
        mock_dataset.__getitem__ = get_item
        
        mock_mnist_dataset.return_value = mock_dataset
        
        sampler = MNISTSampler()
        samples, labels = sampler.sample(10)
        
        assert samples.shape == (10, 1, 32, 32)
        assert labels.shape == (10,)
        assert labels.dtype == torch.int64
    
    @patch('lab_three.datasets.MNIST')
    def test_sample_exceeds_dataset_size(self, mock_mnist_dataset):
        """Test sampling when num_samples exceeds dataset size"""
        mock_dataset = MagicMock()
        mock_dataset.__len__ = lambda x: 5
        mock_mnist_dataset.return_value = mock_dataset
        
        sampler = MNISTSampler()
        
        with pytest.raises(ValueError, match="num_samples exceeds dataset size"):
            sampler.sample(10)
    
    @patch('lab_three.datasets.MNIST')
    def test_sample_single_sample(self, mock_mnist_dataset):
        """Test sampling single sample"""
        mock_dataset = MagicMock()
        mock_dataset.__len__ = lambda x: 100
        mock_samples = [torch.randn(1, 32, 32)]
        mock_labels = [5]
        mock_dataset.__getitem__ = lambda self, idx: (mock_samples[0], mock_labels[0])
        mock_mnist_dataset.return_value = mock_dataset
        
        sampler = MNISTSampler()
        samples, labels = sampler.sample(1)
        
        assert samples.shape == (1, 1, 32, 32)
        assert labels.shape == (1,)
        assert labels[0].item() == 5
    
    @patch('lab_three.datasets.MNIST')
    def test_sample_label_range(self, mock_mnist_dataset):
        """Test that labels are in valid range [0, 9]"""
        mock_dataset = MagicMock()
        mock_dataset.__len__ = lambda x: 100
        
        # Create enough sample data for any possible index
        mock_samples = [torch.randn(1, 32, 32) for _ in range(100)]
        mock_labels = [i % 10 for i in range(100)]
        
        def get_item(self, idx):
            # Handle any index by using modulo
            actual_idx = idx % len(mock_samples)
            return (mock_samples[actual_idx], mock_labels[actual_idx])
        
        mock_dataset.__getitem__ = get_item
        mock_mnist_dataset.return_value = mock_dataset
        
        sampler = MNISTSampler()
        samples, labels = sampler.sample(10)
        
        assert torch.all(labels >= 0)
        assert torch.all(labels <= 9)

