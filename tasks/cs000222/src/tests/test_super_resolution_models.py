"""
Unit tests for super-resolution models module.
"""

import unittest
import torch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from super_resolution.models import SRCNN, FSRCNN


class TestSRCNN(unittest.TestCase):
    """Test SRCNN model."""
    
    def test_srcnn_forward_shape(self):
        """Test SRCNN forward pass output shape."""
        model = SRCNN(scale_factor=2)
        x = torch.randn(2, 1, 32, 32)
        output = model(x)
        self.assertEqual(output.shape[0], 2)
        self.assertEqual(output.shape[1], 1)
        self.assertEqual(output.shape[2], 64)


class TestFSRCNN(unittest.TestCase):
    """Test FSRCNN model."""
    
    def test_fsrcnn_forward_shape(self):
        """Test FSRCNN forward pass output shape."""
        model = FSRCNN(scale_factor=2)
        x = torch.randn(2, 1, 32, 32)
        output = model(x)
        self.assertEqual(output.shape[0], 2)
        self.assertEqual(output.shape[1], 1)
        self.assertEqual(output.shape[2], 64)


if __name__ == '__main__':
    unittest.main()
