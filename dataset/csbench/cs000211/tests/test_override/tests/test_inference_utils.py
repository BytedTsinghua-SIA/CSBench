"""
Test inference utilities
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock dependencies before importing
from unittest.mock import MagicMock
sys.modules['torch'] = MagicMock()

from inference_utils import parse_true_output
from config import InferenceConfig


class TestInferenceUtils(unittest.TestCase):
    """Test inference utility functions"""

    def test_parse_true_output_with_assistant_header(self):
        """Test parsing output containing assistant header"""
        text = (
            "<|start_header_id|>user<|end_header_id|>\n\n"
            "Hello<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
            "Hi there! How can I help you?<|eot_id|>"
        )
        result = parse_true_output(text)
        self.assertEqual(result, "Hi there! How can I help you?")

    def test_parse_true_output_without_eot(self):
        """Test output without eot_id marker"""
        text = (
            "<|start_header_id|>user<|end_header_id|>\n\n"
            "Hello<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
            "Hi there! How can I help you?"
        )
        result = parse_true_output(text)
        self.assertEqual(result, "Hi there! How can I help you?")

    def test_parse_true_output_fallback(self):
        """Test fallback to generic header case"""
        text = (
            "<|start_header_id|>user<|end_header_id|>\n\n"
            "Hello<|eot_id|>"
            "<|end_header_id|>\n\n"
            "This is the response"
        )
        result = parse_true_output(text)
        self.assertEqual(result, "This is the response")

    def test_parse_true_output_no_header(self):
        """Test case with no header"""
        text = "Just plain text response"
        result = parse_true_output(text)
        self.assertEqual(result, "Just plain text response")

    def test_parse_true_output_strips_whitespace(self):
        """Test stripping leading and trailing whitespace"""
        text = (
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
            "  Response with spaces  <|eot_id|>"
        )
        result = parse_true_output(text)
        self.assertEqual(result, "Response with spaces")

    def test_inference_config_defaults(self):
        """Test inference configuration default values"""
        config = InferenceConfig()
        self.assertTrue(config.do_sample)
        self.assertEqual(config.max_new_tokens, 100)
        self.assertTrue(config.use_cache)
        self.assertEqual(config.temperature, 1.5)
        self.assertEqual(config.top_p, 0.9)
        self.assertEqual(config.top_k, 30)

    def test_inference_config_custom(self):
        """Test custom inference configuration"""
        config = InferenceConfig(
            do_sample=False,
            max_new_tokens=200,
            temperature=0.7,
            top_p=0.95,
            top_k=50
        )
        self.assertFalse(config.do_sample)
        self.assertEqual(config.max_new_tokens, 200)
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.top_p, 0.95)
        self.assertEqual(config.top_k, 50)


if __name__ == "__main__":
    unittest.main()

