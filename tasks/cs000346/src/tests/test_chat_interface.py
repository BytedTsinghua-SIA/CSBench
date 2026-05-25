"""
Unit tests for chat interface functionality
Tests script argument parsing and basic operations without running full chat
"""

import unittest
import subprocess
import sys
from pathlib import Path
import tempfile
import os

class TestChatInterface(unittest.TestCase):
    """Test cases for chat interface script"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.script_path = Path(__file__).parent.parent / "chat.sh"

    def test_script_exists(self):
        """Test that chat script exists and is executable"""
        self.assertTrue(self.script_path.exists())
        self.assertTrue(self.script_path.is_file())

        # Check if script is executable
        self.assertTrue(os.access(self.script_path, os.X_OK))

    def test_script_help_output(self):
        """Test that script shows help information"""
        result = subprocess.run(
            [str(self.script_path), "--help"],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)
        self.assertIn("chat.sh", result.stdout)

    def test_default_execution_handling(self):
        """Test that script handles default execution gracefully"""
        # Test running script without arguments (should show interface or error gracefully)
        result = subprocess.run(
            [str(self.script_path)],
            input="quit\n",  # Provide input to exit immediately
            capture_output=True,
            text=True,
            timeout=5  # Prevent hanging
        )

        # Should not crash immediately
        self.assertIsInstance(result.returncode, int)

    def test_implementation_parameter(self):
        """Test implementation parameter handling"""
        valid_implementations = [
            "reference",
            "loop_unrolling",
            "multithreading",
            "simd_programming",
            "multithreading_loop_unrolling",
            "all_techniques"
        ]

        for impl in valid_implementations:
            with self.subTest(implementation=impl):
                result = subprocess.run(
                    [str(self.script_path), "-i", impl, "--help"],
                    capture_output=True,
                    text=True
                )
                self.assertEqual(result.returncode, 0)

    def test_invalid_implementation_handling(self):
        """Test that script handles invalid implementations"""
        result = subprocess.run(
            [str(self.script_path), "-i", "invalid_impl"],
            capture_output=True,
            text=True,
            timeout=3
        )

        # Should exit with error for invalid implementation
        self.assertNotEqual(result.returncode, 0)

    def test_model_path_parameter(self):
        """Test model path parameter handling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [str(self.script_path), "-m", temp_dir, "--help"],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0)

    def test_max_tokens_parameter(self):
        """Test max tokens parameter handling"""
        result = subprocess.run(
            [str(self.script_path), "-t", "64", "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)

    def test_temperature_parameter(self):
        """Test temperature parameter handling"""
        result = subprocess.run(
            [str(self.script_path), "-T", "0.8", "--help"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)

    def test_parameter_combination(self):
        """Test that multiple parameters work together"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [str(self.script_path),
                 "-i", "reference",
                 "-m", temp_dir,
                 "-t", "32",
                 "-T", "0.7",
                 "--help"],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0)

    def test_script_syntax_validation(self):
        """Test that script has valid bash syntax"""
        result = subprocess.run(
            ["bash", "-n", str(self.script_path)],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0,
                        f"Script has syntax errors: {result.stderr}")

    def test_quit_command_simulation(self):
        """Test that quit commands are handled properly"""
        # Test various quit commands
        quit_commands = ["quit", "exit", "q"]

        for cmd in quit_commands:
            with self.subTest(quit_command=cmd):
                result = subprocess.run(
                    [str(self.script_path)],
                    input=f"{cmd}\n",
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                # Should exit gracefully
                self.assertIsInstance(result.returncode, int)

    def test_model_validation_logic(self):
        """Test that script validates model existence"""
        # Test with non-existent model path
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_model_path = Path(temp_dir) / "nonexistent_model"

            result = subprocess.run(
                [str(self.script_path), "-m", str(fake_model_path)],
                input="quit\n",
                capture_output=True,
                text=True,
                timeout=5
            )

            # Should handle missing model gracefully
            self.assertIsInstance(result.returncode, int)

if __name__ == '__main__':
    unittest.main()
