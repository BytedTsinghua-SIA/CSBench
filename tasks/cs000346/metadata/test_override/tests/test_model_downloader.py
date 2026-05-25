"""
Unit tests for model downloader functionality
Tests script argument parsing and basic operations without actual downloads
"""

import unittest
import subprocess
import sys
from pathlib import Path
import tempfile
import os


class TestModelDownloader(unittest.TestCase):
    """Test cases for model downloader script"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.script_path = (
            Path(__file__).parent.parent / "transformer" / "download_model.py"
        )

    def test_script_exists(self):
        """Test that download script exists"""
        self.assertTrue(self.script_path.exists())
        self.assertTrue(self.script_path.is_file())

    def test_script_executable(self):
        """Test that script can be executed with python"""
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())

    def test_help_output(self):
        """Test that script shows help information"""
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--help"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Download LLaMA2 models for TinyChatEngine", result.stdout)
        self.assertIn("--model", result.stdout)
        self.assertIn("--QM", result.stdout)

    def test_list_functionality(self):
        """Test that list option works"""
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--list"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Available Models:", result.stdout)

    def test_missing_required_args(self):
        """Test that script requires necessary arguments"""
        # Test missing model argument
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--QM", "QM_x86"],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)

        # Test missing QM argument
        result = subprocess.run(
            [sys.executable, str(self.script_path), "--model", "LLaMA_7B_2_chat"],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)

    def test_invalid_model_name(self):
        """Test handling of invalid model names"""
        result = subprocess.run(
            [
                sys.executable,
                str(self.script_path),
                "--model",
                "invalid_model",
                "--QM",
                "QM_x86",
            ],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stdout.lower())

    def test_invalid_quantization_method(self):
        """Test handling of invalid quantization methods"""
        result = subprocess.run(
            [
                sys.executable,
                str(self.script_path),
                "--model",
                "LLaMA_7B_2_chat",
                "--QM",
                "invalid_qm",
            ],
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not supported", result.stdout.lower())

    def test_valid_arguments_accepted(self):
        """Test that valid arguments are accepted"""
        # Test x86 quantization
        result = subprocess.run(
            [
                sys.executable,
                str(self.script_path),
                "--model",
                "LLaMA_7B_2_chat",
                "--QM",
                "QM_x86",
                "--help",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)

        # Test ARM quantization
        result = subprocess.run(
            [
                sys.executable,
                str(self.script_path),
                "--model",
                "LLaMA_7B_2_chat",
                "--QM",
                "QM_ARM",
                "--help",
            ],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)

    def test_script_syntax_validation(self):
        """Test that script has valid Python syntax"""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(self.script_path)],
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.returncode, 0, f"Script has syntax errors: {result.stderr}"
        )

    def test_import_functionality(self):
        """Test that script can be imported as module"""
        # Test importing the script (should not execute main)
        import sys

        script_dir = self.script_path.parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))

        try:
            import download_model

            # Test that ModelDownloader class exists
            self.assertTrue(hasattr(download_model, "ModelDownloader"))
            # Test that class can be instantiated
            downloader = download_model.ModelDownloader()
            self.assertIsInstance(downloader, download_model.ModelDownloader)
        finally:
            # Clean up
            if "download_model" in sys.modules:
                del sys.modules["download_model"]


if __name__ == "__main__":
    unittest.main()
