"""
Test model utilities
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock dependencies before importing
from unittest.mock import Mock, patch, MagicMock
sys.modules['torch'] = MagicMock()
sys.modules['unsloth'] = MagicMock()
sys.modules['unsloth.chat_templates'] = MagicMock()
sys.modules['unsloth.chat_templates'].get_chat_template = MagicMock(return_value=lambda x, **kwargs: x)
sys.modules['unsloth'].FastLanguageModel = MagicMock()

from model_utils import (
    setup_chat_template,
    enable_inference_mode,
    save_model,
    load_model
)
from config import ModelConfig, LoRAConfig


class TestModelUtils(unittest.TestCase):
    """Test model utility functions"""

    def test_setup_chat_template(self):
        """Test setting chat template"""
        mock_tokenizer = Mock()
        mock_tokenizer.apply_chat_template = Mock(return_value="formatted")

        result = setup_chat_template(mock_tokenizer, "llama-3.1")
        # Since get_chat_template returns tokenizer, we check if it was called
        # In actual implementation, get_chat_template modifies tokenizer and returns it
        self.assertIsNotNone(result)

    @patch('model_utils.FastLanguageModel')
    def test_enable_inference_mode(self, mock_fast_lm):
        """Test enabling inference mode"""
        mock_model = Mock()
        enable_inference_mode(mock_model)
        mock_fast_lm.for_inference.assert_called_once_with(mock_model)

    def test_save_model(self):
        """Test saving model"""
        mock_model = Mock()
        mock_tokenizer = Mock()
        save_path = "test_model"

        save_model(mock_model, mock_tokenizer, save_path)
        mock_model.save_pretrained.assert_called_once_with(save_path)
        mock_tokenizer.save_pretrained.assert_called_once_with(save_path)

    @patch('model_utils.FastLanguageModel')
    def test_load_model(self, mock_fast_lm):
        """Test loading model"""
        mock_model = Mock()
        mock_tokenizer = Mock()
        mock_fast_lm.from_pretrained.return_value = (mock_model, mock_tokenizer)

        model_config = ModelConfig()
        result_model, result_tokenizer = load_model("test_path", model_config)

        mock_fast_lm.from_pretrained.assert_called_once()
        self.assertEqual(result_model, mock_model)
        self.assertEqual(result_tokenizer, mock_tokenizer)

    def test_model_config(self):
        """Test model configuration"""
        config = ModelConfig(
            model_name="test_model",
            max_seq_length=4096,
            dtype="float16",
            load_in_4bit=False
        )
        self.assertEqual(config.model_name, "test_model")
        self.assertEqual(config.max_seq_length, 4096)
        self.assertEqual(config.dtype, "float16")
        self.assertFalse(config.load_in_4bit)

    def test_lora_config(self):
        """Test LoRA configuration"""
        config = LoRAConfig(
            r=32,
            lora_alpha=32,
            lora_dropout=0.1
        )
        self.assertEqual(config.r, 32)
        self.assertEqual(config.lora_alpha, 32)
        self.assertEqual(config.lora_dropout, 0.1)


if __name__ == "__main__":
    unittest.main()

