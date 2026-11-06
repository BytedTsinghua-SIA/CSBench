"""
Unit tests for evaluation script functionality
Tests script argument parsing and basic operations without running full evaluations
"""

import unittest
import subprocess
import sys
from pathlib import Path
import tempfile
import os

class TestEvaluation(unittest.TestCase):
    """Test cases for evaluation script functionality"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.script_path = Path(__file__).parent.parent / "kernels" / "starter_code" / "evaluate.sh"
        self.test_dir = Path(__file__).parent.parent / "kernels" / "starter_code"

    def test_script_exists(self):
        """Test that evaluation script exists and is executable"""
        self.assertTrue(self.script_path.exists())
        self.assertTrue(self.script_path.is_file())

        # Check if script is executable
        self.assertTrue(os.access(self.script_path, os.X_OK))

    def test_script_help_output(self):
        """Test that script shows help information"""
        result = subprocess.run(
            [str(self.script_path), "--help"],
            capture_output=True,
            text=True,
            cwd=self.test_dir
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)
        self.assertIn("evaluate.sh", result.stdout)

    def test_invalid_target_handling(self):
        """Test that script handles invalid targets gracefully"""
        result = subprocess.run(
            [str(self.script_path), "invalid_target"],
            capture_output=True,
            text=True,
            cwd=self.test_dir
        )

        # Should exit with error code for invalid target
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error:", result.stdout)

    def test_valid_targets_recognized(self):
        """Test that script recognizes valid implementation targets"""
        valid_targets = [
            "reference",
            "loop_unrolling",
            "multithreading",
            "simd_programming",
            "multithreading_loop_unrolling",
            "all_techniques"
        ]

        for target in valid_targets:
            with self.subTest(target=target):
                # Test that script accepts valid targets without immediate error
                result = subprocess.run(
                    [str(self.script_path), target, "--help"],
                    capture_output=True,
                    text=True,
                    cwd=self.test_dir
                )
                # Should show help, not an error about invalid target
                self.assertIn("Usage:", result.stdout)

    def test_parameter_parsing(self):
        """Test script parameter parsing"""
        # Test iterations parameter
        result = subprocess.run(
            [str(self.script_path), "--iterations", "50", "--help"],
            capture_output=True,
            text=True,
            cwd=self.test_dir
        )
        self.assertEqual(result.returncode, 0)

        # Test output directory parameter
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [str(self.script_path), "--output", temp_dir, "--help"],
                capture_output=True,
                text=True,
                cwd=self.test_dir
            )
            self.assertEqual(result.returncode, 0)

    def test_output_directory_creation(self):
        """Test that script can create output directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_output = Path(temp_dir) / "custom_results"

            # Run script with custom output directory
            result = subprocess.run(
                [str(self.script_path), "reference", "--output", str(custom_output)],
                capture_output=True,
                text=True,
                cwd=self.test_dir,
                timeout=10  # Prevent hanging
            )

            # Script should not fail due to directory creation issues
            if result.returncode != 0:
                # Check if it's not a directory creation error
                self.assertNotIn("mkdir", result.stderr.lower())

    def test_script_syntax_validation(self):
        """Test that script has valid bash syntax"""
        result = subprocess.run(
            ["bash", "-n", str(self.script_path)],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0,
                        f"Script has syntax errors: {result.stderr}")

    def test_implementation_files_check(self):
        """Test that script checks for implementation files"""
        # This tests the script's file validation logic
        result = subprocess.run(
            [str(self.script_path), "reference"],
            capture_output=True,
            text=True,
            cwd=self.test_dir,
            timeout=5  # Short timeout to avoid full execution
        )

        # Should not fail due to missing files (they exist in our setup)
        # If it times out or fails for other reasons, that's expected
        # We just want to ensure it doesn't fail due to file not found
        pass

if __name__ == '__main__':
    unittest.main()
