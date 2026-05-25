"""
Test dataset utilities
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock datasets before importing
from unittest.mock import MagicMock
sys.modules['datasets'] = MagicMock()
sys.modules['unsloth'] = MagicMock()
sys.modules['unsloth.chat_templates'] = MagicMock()
sys.modules['unsloth.chat_templates'].standardize_sharegpt = MagicMock(side_effect=lambda x: x)

# Import Dataset class - we'll use a simple mock implementation
from datasets import Dataset
from dataset_utils import (
    add_text_field,
    compute_conversation_length,
    advanced_sort_key,
    sort_dataset_simple,
    sort_dataset_advanced,
    create_formatting_prompts_func
)


class TestDatasetUtils(unittest.TestCase):
    """Test dataset utility functions"""

    def setUp(self):
        """Set up test data"""
        self.sample_example = {
            "id": "test_1",
            "conversations": [
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "assistant", "content": "I'm doing well, thank you!"}
            ],
            "score": 0.8
        }

        self.dataset_data = [
            {
                "id": "id_1",
                "conversations": [
                    {"role": "user", "content": "Short question"},
                    {"role": "assistant", "content": "Short answer"}
                ],
                "score": 0.5
            },
            {
                "id": "id_2",
                "conversations": [
                    {"role": "user", "content": "This is a much longer question with more words"},
                    {"role": "assistant", "content": "This is a much longer answer with many more words"}
                ],
                "score": 0.9
            },
            {
                "id": "id_3",
                "conversations": [
                    {"role": "user", "content": "Medium length question here"},
                    {"role": "assistant", "content": "Medium length answer"}
                ],
                "score": 0.7
            }
        ]

    def test_add_text_field(self):
        """Test add_text_field function"""
        result = add_text_field(self.sample_example)
        self.assertIn("text", result)
        self.assertEqual(result["text"], "I'm doing well, thank you!")

    def test_add_text_field_no_assistant(self):
        """Test case with no assistant message"""
        example = {
            "id": "test_2",
            "conversations": [
                {"role": "user", "content": "Hello"}
            ]
        }
        result = add_text_field(example)
        self.assertEqual(result["text"], "")

    def test_compute_conversation_length(self):
        """Test compute_conversation_length function"""
        length = compute_conversation_length(self.sample_example)
        # "Hello, how are you?" = 4 words
        # "I'm doing well, thank you!" = 5 words
        # Total = 9 words
        self.assertEqual(length, 9)

    def test_compute_conversation_length_empty(self):
        """Test length of empty conversation"""
        example = {
            "id": "test_3",
            "conversations": []
        }
        length = compute_conversation_length(example)
        self.assertEqual(length, 0)

    def test_advanced_sort_key(self):
        """Test advanced_sort_key function"""
        key_value = advanced_sort_key(self.sample_example)
        # conversation_len = 9
        # score = 0.8
        # key = 1e-5 * 9 + 0.8 * 1 = 0.00009 + 0.8 = 0.80009
        expected = 1e-5 * 9 + 0.8 * 1
        self.assertAlmostEqual(key_value, expected, places=5)

    def test_advanced_sort_key_no_score(self):
        """Test case with no score field"""
        example = {
            "id": "test_4",
            "conversations": [
                {"role": "user", "content": "Test"},
                {"role": "assistant", "content": "Answer"}
            ]
        }
        key_value = advanced_sort_key(example)
        # conversation_len = 2
        # score = 0.0 (default)
        # key = 1e-5 * 2 + 0.0 * 1 = 0.00002
        expected = 1e-5 * 2
        self.assertAlmostEqual(key_value, expected, places=5)

    def test_sort_dataset_simple(self):
        """Test simple sorting"""
        dataset = Dataset.from_list(self.dataset_data)
        sorted_dataset = sort_dataset_simple(dataset)

        # Check if sorted by length (from short to long)
        lengths = [
            compute_conversation_length(sorted_dataset[i])
            for i in range(len(sorted_dataset))
        ]
        self.assertEqual(lengths, sorted(lengths))

    def test_sort_dataset_advanced(self):
        """Test advanced sorting"""
        dataset = Dataset.from_list(self.dataset_data)
        sorted_dataset = sort_dataset_advanced(dataset)

        # Check if sorted by advanced key (from high to low)
        keys = [
            advanced_sort_key(sorted_dataset[i])
            for i in range(len(sorted_dataset))
        ]
        self.assertEqual(keys, sorted(keys, reverse=True))

    def test_create_formatting_prompts_func(self):
        """Test creating formatting function"""
        # Create a mock tokenizer
        class MockTokenizer:
            def apply_chat_template(self, convo, tokenize=False, add_generation_prompt=False):
                return f"Formatted: {convo}"

        tokenizer = MockTokenizer()
        formatting_func = create_formatting_prompts_func(tokenizer)

        # Test formatting function
        examples = {
            "conversations": [
                [{"role": "user", "content": "Hello"}],
                [{"role": "user", "content": "Hi"}]
            ]
        }
        result = formatting_func(examples)
        self.assertIn("text", result)
        self.assertEqual(len(result["text"]), 2)


if __name__ == "__main__":
    unittest.main()

