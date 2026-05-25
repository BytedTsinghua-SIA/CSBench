"""
Unit tests for super-resolution evaluation module.
"""

import unittest
import torch
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from super_resolution.evaluate import compute_psnr, compute_ssim


class TestComputePSNR(unittest.TestCase):
    """Test compute_psnr function."""
    
    def test_compute_psnr_identical_images(self):
        """Test PSNR for identical images."""
        img1 = torch.ones(1, 1, 32, 32) * 0.5
        img2 = torch.ones(1, 1, 32, 32) * 0.5
        psnr = compute_psnr(img1, img2)
        self.assertEqual(psnr, float('inf'))


class TestComputeSSIM(unittest.TestCase):
    """Test compute_ssim function."""
    
    def test_compute_ssim_identical_images(self):
        """Test SSIM for identical images."""
        img1 = torch.ones(1, 1, 32, 32) * 0.5
        img2 = torch.ones(1, 1, 32, 32) * 0.5
        ssim = compute_ssim(img1, img2)
        self.assertAlmostEqual(ssim, 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
