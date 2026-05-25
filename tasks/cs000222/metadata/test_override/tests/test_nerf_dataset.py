"""
Unit tests for NeRF dataset module.
"""

import unittest
import torch
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nerf.dataset import pose_spherical, get_rays


class TestPoseSpherical(unittest.TestCase):
    """Test pose_spherical function."""
    
    def test_pose_spherical_returns_matrix(self):
        """Test pose_spherical returns 4x4 matrix."""
        pose = pose_spherical(0.0, 0.0, 1.0)
        self.assertEqual(pose.shape, (4, 4))
        self.assertIsInstance(pose, np.ndarray)


class TestGetRays(unittest.TestCase):
    """Test get_rays function."""
    
    def test_get_rays_output_shapes(self):
        """Test get_rays output shapes."""
        H, W = 64, 64
        focal = 100.0
        pose = torch.eye(4)
        rays_o, rays_d = get_rays(H, W, focal, pose)
        self.assertEqual(rays_o.shape, (H, W, 3))
        self.assertEqual(rays_d.shape, (H, W, 3))


if __name__ == '__main__':
    unittest.main()
