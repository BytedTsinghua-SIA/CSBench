"""
Unit tests for IsotropicGaussian
"""
import pytest
import torch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab_three import IsotropicGaussian


class TestIsotropicGaussian:
    """Test cases for IsotropicGaussian"""
    
    def test_initialization(self):
        """Test IsotropicGaussian initialization"""
        gaussian = IsotropicGaussian(shape=[1, 32, 32], std=1.0)
        
        assert gaussian.shape == [1, 32, 32]
        assert gaussian.std == 1.0
    
    def test_sample_output_shape(self):
        """Test sample output shape with different configurations"""
        # Test different shapes and batch sizes
        shapes = [[1, 32, 32], [1, 16, 16]]
        for shape in shapes:
            gaussian = IsotropicGaussian(shape=shape, std=1.0)
            for bs in [1, 4]:
                samples, labels = gaussian.sample(bs)
                assert samples.shape == (bs, *shape)
                assert labels is None
        
        # Test different std values
        for std in [0.5, 1.0, 2.0]:
            gaussian = IsotropicGaussian(shape=[1, 32, 32], std=std)
            samples, labels = gaussian.sample(100)
            sample_std = samples.std().item()
            assert abs(sample_std - std) < 0.5
            assert labels is None

