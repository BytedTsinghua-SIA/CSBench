"""
Unit tests for inference module - Simplified
"""

import unittest
import tempfile
import os
import json
import csv
from unittest.mock import Mock, patch
import sys

# Tests are now inside src/tests
tests_path = os.path.dirname(__file__)
sys.path.insert(0, tests_path)
from test_helpers import setup_test_imports

modules = setup_test_imports()

# Import functions and classes
get_response = modules["inference"].get_response
evaluate_gsm8k_public = modules["inference"].evaluate_gsm8k_public
DataConfig = modules["config"].DataConfig


class TestGetResponse(unittest.TestCase):
    """Test get_response function"""

    def test_get_response(self):
        """Test getting response from generator"""
        # Mock generator
        mock_generator = Mock()
        mock_generator.return_value = [
            {
                "generated_text": [
                    {"role": "user", "content": "Q: Test"},
                    {"role": "assistant", "content": "A: 42"},
                ]
            }
        ]

        chats = [{"role": "user", "content": "Q: Test"}]
        result = get_response(mock_generator, chats)

        self.assertEqual(result, "A: 42")
        mock_generator.assert_called_once_with(chats)


class TestEvaluateGsm8kPublic(unittest.TestCase):
    """Test evaluate_gsm8k_public function"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary test files
        self.test_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        self.train_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )

        # Write test data
        test_data = [
            {"question": "Q1", "answer": "A: 10 #### 10"},
            {"question": "Q2", "answer": "A: 20 #### 20"},
        ]
        for item in test_data:
            self.test_file.write(json.dumps(item) + "\n")
        self.test_file.close()

        train_data = [
            {"question": "Train Q1", "answer": "Train A1"},
            {"question": "Train Q2", "answer": "Train A2"},
        ]
        for item in train_data:
            self.train_file.write(json.dumps(item) + "\n")
        self.train_file.close()

    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.test_file.name)
        os.unlink(self.train_file.name)

    def test_evaluate_gsm8k_public_correct(self):
        """Test evaluation with correct predictions"""
        # Mock generator
        mock_generator = Mock()

        # Patch the functions in the inference module
        with patch.object(
            modules["inference"], "get_response"
        ) as mock_get_response, patch.object(
            modules["inference"], "nshot_chats"
        ) as mock_nshot_chats:

            # Mock responses
            mock_get_response.side_effect = ["A: 10 #### 10", "A: 20 #### 20"]
            mock_nshot_chats.return_value = [{"role": "user", "content": "Q: Test"}]

            data_config = DataConfig(test_n_shot=1, use_fixed_few_shot=False)

            predictions, accuracy = evaluate_gsm8k_public(
                mock_generator, self.test_file.name, self.train_file.name, data_config
            )

            self.assertEqual(len(predictions), 2)
            self.assertEqual(accuracy, 1.0)  # Both correct
            self.assertEqual(mock_get_response.call_count, 2)


if __name__ == "__main__":
    unittest.main()
