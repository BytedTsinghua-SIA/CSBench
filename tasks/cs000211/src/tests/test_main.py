"""
Test main program
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock dependencies before importing modules that need them
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock torch and other heavy dependencies
sys.modules['torch'] = MagicMock()
sys.modules['unsloth'] = MagicMock()
sys.modules['unsloth.chat_templates'] = MagicMock()
sys.modules['unsloth.chat_templates'].get_chat_template = MagicMock(return_value=lambda x, **kwargs: x)
sys.modules['unsloth.chat_templates'].standardize_sharegpt = MagicMock(side_effect=lambda x: x)
sys.modules['unsloth.chat_templates'].train_on_responses_only = MagicMock(side_effect=lambda x: x)
sys.modules['unsloth'].FastLanguageModel = MagicMock()
sys.modules['unsloth'].is_bfloat16_supported = MagicMock(return_value=False)
sys.modules['trl'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['datasets'] = MagicMock()

from main import main
from config import Config


class TestMain(unittest.TestCase):
    """Test main program"""

    @patch('main.run_inference_on_test_set')
    @patch('main.save_model')
    @patch('main.train_model')
    @patch('main.create_trainer')
    @patch('main.prepare_training_dataset')
    @patch('main.create_formatting_prompts_func')
    @patch('main.sort_dataset_advanced')
    @patch('main.sort_dataset_simple')
    @patch('main.load_dataset_from_disk')
    @patch('main.initialize_model')
    def test_main_basic_flow(self, mock_init_model, mock_load_dataset,
                            mock_sort_simple, mock_sort_advanced,
                            mock_create_formatting, mock_prepare_dataset,
                            mock_create_trainer, mock_train_model,
                            mock_save_model, mock_inference):
        """Test basic flow"""
        # Set mock return values
        mock_model = Mock()
        mock_tokenizer = Mock()
        mock_init_model.return_value = (mock_model, mock_tokenizer)

        mock_dataset = Mock()
        mock_dataset.__len__ = Mock(return_value=100)  # Make len() work
        mock_load_dataset.return_value = mock_dataset

        mock_sorted_simple = Mock()
        mock_sorted_advanced = Mock()
        mock_sort_simple.return_value = mock_sorted_simple
        mock_sort_advanced.return_value = mock_sorted_advanced

        mock_formatting_func = Mock()
        mock_create_formatting.return_value = mock_formatting_func

        mock_train_dataset = Mock()
        mock_train_dataset.__len__ = Mock(return_value=50)  # Make len() work
        mock_prepare_dataset.return_value = mock_train_dataset

        mock_trainer = Mock()
        mock_create_trainer.return_value = mock_trainer

        mock_train_stats = {"loss": 0.5}
        mock_train_model.return_value = mock_train_stats

        # Run main function
        config = Config()
        config.dataset.test_set_path = "/fake/path/test.json"
        
        with patch('os.path.exists', return_value=False):
            main(config, use_curriculum=False)

        # Verify calls
        mock_init_model.assert_called_once()
        mock_load_dataset.assert_called_once()
        mock_sort_simple.assert_called_once()
        mock_sort_advanced.assert_called_once()
        mock_prepare_dataset.assert_called_once()
        mock_create_trainer.assert_called_once()
        mock_train_model.assert_called_once()
        mock_save_model.assert_called_once()

    def test_config_defaults(self):
        """Test default configuration"""
        config = Config()
        self.assertIsNotNone(config.model)
        self.assertIsNotNone(config.lora)
        self.assertIsNotNone(config.training)
        self.assertIsNotNone(config.inference)
        self.assertIsNotNone(config.dataset)


if __name__ == "__main__":
    unittest.main()

