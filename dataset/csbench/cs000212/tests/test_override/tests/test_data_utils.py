"""
Unit tests for data_utils module
"""

import unittest
import tempfile
import os
import json
import csv
from unittest.mock import patch, MagicMock

import sys

# Tests are now inside src, so we can import directly
sys.path.insert(
    0, os.path.dirname(os.path.dirname(__file__))
)  # Go up from tests to src

from data_utils import load_jsonlines, load_csv, nshot_chats, extract_ans_from_response


class TestLoadJsonlines(unittest.TestCase):
    """Test load_jsonlines function"""

    def test_load_jsonlines_single_line(self):
        """Test loading a single JSON line"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as f:
            data = {"question": "What is 2+2?", "answer": "4"}
            f.write(json.dumps(data) + "\n")
            temp_file = f.name

        try:
            result = load_jsonlines(temp_file)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["question"], "What is 2+2?")
            self.assertEqual(result[0]["answer"], "4")
        finally:
            os.unlink(temp_file)

    def test_load_jsonlines_multiple_lines(self):
        """Test loading multiple JSON lines"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as f:
            data1 = {"question": "Q1", "answer": "A1"}
            data2 = {"question": "Q2", "answer": "A2"}
            f.write(json.dumps(data1) + "\n")
            f.write(json.dumps(data2) + "\n")
            temp_file = f.name

        try:
            result = load_jsonlines(temp_file)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["question"], "Q1")
            self.assertEqual(result[1]["question"], "Q2")
        finally:
            os.unlink(temp_file)

    def test_load_jsonlines_empty_file(self):
        """Test loading an empty file"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as f:
            temp_file = f.name

        try:
            result = load_jsonlines(temp_file)
            self.assertEqual(len(result), 0)
            self.assertIsInstance(result, list)
        finally:
            os.unlink(temp_file)


class TestLoadCsv(unittest.TestCase):
    """Test load_csv function"""

    def test_load_csv_single_row(self):
        """Test loading CSV with single row"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["prompt_text"])
            writer.writeheader()
            writer.writerow({"prompt_text": "What is 2+2?"})
            temp_file = f.name

        try:
            result = load_csv(temp_file)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], "What is 2+2?")
        finally:
            os.unlink(temp_file)

    def test_load_csv_multiple_rows(self):
        """Test loading CSV with multiple rows"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["prompt_text"])
            writer.writeheader()
            writer.writerow({"prompt_text": "Q1"})
            writer.writerow({"prompt_text": "Q2"})
            temp_file = f.name

        try:
            result = load_csv(temp_file)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], "Q1")
            self.assertEqual(result[1], "Q2")
        finally:
            os.unlink(temp_file)


class TestNshotChats(unittest.TestCase):
    """Test nshot_chats function"""

    def setUp(self):
        """Set up test fixtures"""
        self.nshot_data = [
            {"question": "Q1", "answer": "A1"},
            {"question": "Q2", "answer": "A2"},
            {"question": "Q3", "answer": "A3"},
        ]

    def test_nshot_chats_train_mode(self):
        """Test nshot_chats in train mode"""
        with patch("data_utils.random.sample") as mock_sample:
            mock_sample.return_value = [self.nshot_data[0]]

            result = nshot_chats(
                nshot_data=self.nshot_data,
                n=1,
                question="Test Q",
                answer="Test A",
                mode="train",
            )

            # Should have 1 example (user + assistant) + current question + current answer
            self.assertEqual(len(result), 4)
            self.assertEqual(result[0]["role"], "user")
            self.assertEqual(result[1]["role"], "assistant")
            self.assertEqual(result[2]["role"], "user")
            self.assertEqual(result[3]["role"], "assistant")
            self.assertIn("Test Q", result[2]["content"])
            self.assertIn("Test A", result[3]["content"])

    def test_nshot_chats_test_mode(self):
        """Test nshot_chats in test mode"""
        with patch("data_utils.random.sample") as mock_sample:
            mock_sample.return_value = [self.nshot_data[0]]

            result = nshot_chats(
                nshot_data=self.nshot_data,
                n=1,
                question="Test Q",
                answer=None,
                mode="test",
            )

            # Should have 1 example (user + assistant) + current question (no answer)
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]["role"], "user")
            self.assertEqual(result[1]["role"], "assistant")
            self.assertEqual(result[2]["role"], "user")
            self.assertIn("Test Q", result[2]["content"])

    def test_nshot_chats_fixed_examples(self):
        """Test nshot_chats with fixed examples"""
        fixed_examples = [self.nshot_data[0], self.nshot_data[1]]

        result = nshot_chats(
            nshot_data=self.nshot_data,
            n=2,
            question="Test Q",
            answer="Test A",
            mode="train",
            fixed_examples=fixed_examples,
        )

        # Should have 2 examples (4 messages) + current question + current answer
        self.assertEqual(len(result), 6)
        self.assertEqual(result[0]["content"], "Q: Q1")
        self.assertEqual(result[2]["content"], "Q: Q2")

    def test_nshot_chats_invalid_mode(self):
        """Test nshot_chats with invalid mode"""
        with self.assertRaises(ValueError):
            nshot_chats(
                nshot_data=self.nshot_data,
                n=1,
                question="Test Q",
                answer="Test A",
                mode="invalid",
            )

    def test_nshot_chats_train_mode_no_answer(self):
        """Test nshot_chats in train mode without answer"""
        with self.assertRaises(ValueError):
            nshot_chats(
                nshot_data=self.nshot_data,
                n=1,
                question="Test Q",
                answer=None,
                mode="train",
            )


class TestExtractAnsFromResponse(unittest.TestCase):
    """Test extract_ans_from_response function"""

    def test_extract_ans_with_hash(self):
        """Test extracting answer with #### marker"""
        response = "Let's think step by step. The answer is 42. #### 42"
        result = extract_ans_from_response(response)
        self.assertEqual(result, "42")

    def test_extract_ans_with_special_chars(self):
        """Test extracting answer with special characters"""
        response = "Answer: #### $1,234.56"
        result = extract_ans_from_response(response)
        self.assertEqual(result, "1234.56")

    def test_extract_ans_with_percent(self):
        """Test extracting answer with percent sign"""
        response = "Result: #### 50%"
        result = extract_ans_from_response(response)
        self.assertEqual(result, "50")

    def test_extract_ans_with_gram(self):
        """Test extracting answer with 'g' suffix"""
        response = "Weight: #### 100g"
        result = extract_ans_from_response(response)
        self.assertEqual(result, "100")

    def test_extract_ans_no_hash(self):
        """Test extracting answer without #### marker"""
        response = "The answer is 42 in the end."
        result = extract_ans_from_response(response)
        # Should extract the last number
        self.assertEqual(result, "42")

    def test_extract_ans_multiple_numbers(self):
        """Test extracting answer with multiple numbers"""
        response = "First 10, then 20, finally 30"
        result = extract_ans_from_response(response)
        self.assertEqual(result, "30")

    def test_extract_ans_no_numbers(self):
        """Test extracting answer with no numbers"""
        response = "This is just text without numbers"
        result = extract_ans_from_response(response)
        # Should return stripped text
        self.assertEqual(result, "This is just text without numbers")


if __name__ == "__main__":
    unittest.main()
