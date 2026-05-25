"""
Unit tests for model_utils module - Simplified
"""

import unittest
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Tests are now inside src/tests
tests_path = os.path.dirname(__file__)
sys.path.insert(0, tests_path)
from test_helpers import setup_test_imports

modules = setup_test_imports()

# Import functions and classes
setup_device = modules["model_utils"].setup_device
ModelConfig = modules["config"].ModelConfig


class TestSetupDevice(unittest.TestCase):
    """Test setup_device function"""

    @patch.dict(os.environ, {}, clear=False)
    def test_setup_device_default(self):
        """Test setting up device with default value"""
        # Mock torch in the module namespace
        with patch.object(modules["model_utils"], "torch") as mock_torch:
            mock_device = Mock()
            mock_device.__str__ = Mock(return_value="cuda:0")
            mock_torch.device.return_value = mock_device

            device = setup_device()
            self.assertEqual(str(device), "cuda:0")
            self.assertEqual(os.environ.get("CUDA_VISIBLE_DEVICES"), "0")


if __name__ == "__main__":
    unittest.main()
