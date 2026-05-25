"""
Unit tests for NeRF models module.
"""

import unittest
import torch
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nerf.models import PositionalEncoding, NeRF, sample_points_along_rays


class TestPositionalEncoding(unittest.TestCase):
    """Test PositionalEncoding class."""
    
    def test_positional_encoding_forward_shape(self):
        """Test PositionalEncoding forward pass output shape."""
        encoding = PositionalEncoding(num_freqs=5, include_input=True)
        x = torch.randn(10, 3)
        encoded = encoding(x)
        expected_dim = 3 + 6 * 5
        self.assertEqual(encoded.shape[-1], expected_dim)


class TestNeRF(unittest.TestCase):
    """Test NeRF model."""
    
    def test_nerf_forward_output_keys(self):
        """Test NeRF forward pass returns correct keys."""
        model = NeRF(num_layers=4, hidden_dim=64)
        xyz = torch.randn(10, 3)
        viewdirs = torch.randn(10, 3)
        output = model(xyz, viewdirs)
        self.assertIn('rgb', output)
        self.assertIn('density', output)


class TestSamplePointsAlongRays(unittest.TestCase):
    """Test sample_points_along_rays function."""
    
    def test_sample_points_shape(self):
        """Test sample_points_along_rays output shapes."""
        rays_o = torch.randn(5, 3)
        rays_d = torch.randn(5, 3)
        num_samples = 32
        points, t_vals = sample_points_along_rays(rays_o, rays_d, 0.0, 1.0, num_samples)
        self.assertEqual(points.shape, (5, num_samples, 3))
        self.assertEqual(t_vals.shape, (5, num_samples))


if __name__ == '__main__':
    unittest.main()
