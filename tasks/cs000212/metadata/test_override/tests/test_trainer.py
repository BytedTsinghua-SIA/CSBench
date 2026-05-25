"""
Unit tests for trainer module - Simplified
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch
import sys

# Tests are now inside src/tests
tests_path = os.path.dirname(__file__)
sys.path.insert(0, tests_path)
from test_helpers import setup_test_imports

modules = setup_test_imports()

# Import functions and classes
format_gsm8k_data = modules["trainer"].format_gsm8k_data
DataConfig = modules["config"].DataConfig


class TestFormatGsm8kData(unittest.TestCase):
    """Test format_gsm8k_data function"""

    def setUp(self):
        """Set up test fixtures"""
        self.train_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        train_data = [
            {"question": "Q1", "answer": "A: 10 #### 10"},
            {"question": "Q2", "answer": "A: 20 #### 20"},
        ]
        for item in train_data:
            self.train_file.write(json.dumps(item) + "\n")
        self.train_file.close()

    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.train_file.name)

    def test_format_gsm8k_data(self):
        """Test formatting GSM8K data"""
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.apply_chat_template.return_value = (
            "formatted_text<|eot_id|>actual_text"
        )
        mock_tokenizer.return_value = {"input_ids": [1, 2, 3, 4, 5]}

        data_config = DataConfig(train_n_shot=1, use_fixed_few_shot=False)

        # Patch nshot_chats and Dataset
        with patch.object(
            modules["trainer"], "nshot_chats"
        ) as mock_nshot_chats, patch.object(
            modules["trainer"], "Dataset"
        ) as mock_dataset_class:

            # Mock nshot_chats
            mock_nshot_chats.return_value = [
                {"role": "user", "content": "Q: Q1"},
                {"role": "assistant", "content": "A: A1"},
            ]

            # Mock Dataset.from_list
            mock_dataset_instance = Mock()
            mock_dataset_instance.__len__ = Mock(return_value=2)
            mock_dataset_class.from_list.return_value = mock_dataset_instance

            dataset, max_token_len = format_gsm8k_data(
                mock_tokenizer, self.train_file.name, data_config
            )

            self.assertEqual(len(dataset), 2)
            self.assertGreater(max_token_len, 0)
            self.assertEqual(mock_nshot_chats.call_count, 2)


if __name__ == "__main__":
    unittest.main()
