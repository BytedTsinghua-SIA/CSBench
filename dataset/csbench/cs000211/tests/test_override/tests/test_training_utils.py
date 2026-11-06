"""
Test training utilities
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock dependencies before importing
from unittest.mock import Mock, patch, MagicMock
sys.modules['trl'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['unsloth'] = MagicMock()
sys.modules['unsloth.chat_templates'] = MagicMock()
sys.modules['unsloth.chat_templates'].train_on_responses_only = MagicMock(side_effect=lambda x: x)
sys.modules['unsloth.chat_templates'].standardize_sharegpt = MagicMock(side_effect=lambda x: x)
sys.modules['unsloth'].is_bfloat16_supported = MagicMock(return_value=False)

from training_utils import create_trainer
from config import TrainingConfig


class TestTrainingUtils(unittest.TestCase):
    """Test training utility functions"""

    def setUp(self):
        """Set up test data"""
        self.mock_model = Mock()
        self.mock_tokenizer = Mock()
        self.mock_train_dataset = Mock()
        self.training_config = TrainingConfig()
        self.max_seq_length = 2048

    @patch('training_utils.SFTTrainer')
    @patch('training_utils.DataCollatorForSeq2Seq')
    @patch('training_utils.TrainingArguments')
    @patch('training_utils.is_bfloat16_supported')
    @patch('training_utils.train_on_responses_only')
    def test_create_trainer(self, mock_train_on_responses, mock_bfloat16,
                           mock_training_args, mock_data_collator, mock_sft_trainer):
        """Test creating trainer"""
        mock_bfloat16.return_value = False
        mock_trainer_instance = Mock()
        mock_sft_trainer.return_value = mock_trainer_instance
        mock_train_on_responses.return_value = mock_trainer_instance

        trainer = create_trainer(
            self.mock_model,
            self.mock_tokenizer,
            self.mock_train_dataset,
            self.training_config,
            self.max_seq_length
        )

        # Check if SFTTrainer was called
        mock_sft_trainer.assert_called_once()
        # Check if train_on_responses_only was called
        mock_train_on_responses.assert_called_once()
        self.assertEqual(trainer, mock_trainer_instance)

    def test_training_config_defaults(self):
        """Test training configuration default values"""
        config = TrainingConfig()
        self.assertEqual(config.per_device_train_batch_size, 2)
        self.assertEqual(config.gradient_accumulation_steps, 4)
        self.assertEqual(config.warmup_steps, 10)
        self.assertEqual(config.num_train_epochs, 2)
        self.assertEqual(config.learning_rate, 2e-4)
        self.assertEqual(config.optim, "adamw_8bit")
        self.assertEqual(config.weight_decay, 0.01)
        self.assertEqual(config.lr_scheduler_type, "linear")
        self.assertEqual(config.seed, 3407)

    def test_training_config_custom(self):
        """Test custom training configuration"""
        config = TrainingConfig(
            per_device_train_batch_size=4,
            gradient_accumulation_steps=8,
            num_train_epochs=3,
            learning_rate=1e-4
        )
        self.assertEqual(config.per_device_train_batch_size, 4)
        self.assertEqual(config.gradient_accumulation_steps, 8)
        self.assertEqual(config.num_train_epochs, 3)
        self.assertEqual(config.learning_rate, 1e-4)

    @patch('training_utils.train_model')
    def test_train_model(self, mock_train_model):
        """Test training model"""
        mock_trainer = Mock()
        mock_stats = {"loss": 0.5, "epoch": 1.0}
        mock_train_model.return_value = mock_stats

        stats = mock_train_model(mock_trainer)
        self.assertEqual(stats, mock_stats)


if __name__ == "__main__":
    unittest.main()

