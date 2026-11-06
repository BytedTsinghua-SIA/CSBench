import unittest
import os
try:
    from .test_utils import ProgramRunner
except ImportError:
    from test_utils import ProgramRunner


class TestPolarisCommunicationSystem(unittest.TestCase):
    """Unit tests for Polaris satellite communication system"""

    def setUp(self):
        """Set up test environment"""
        self.runner = ProgramRunner(os.path.join(os.path.dirname(__file__), '..', 'polaris'))

    def test_program_exists(self):
        """Test that polaris program exists and is executable"""
        self.assertTrue(os.path.exists(self.runner.program_path))

    def test_no_arguments_error(self):
        """Test program behavior with no arguments"""
        exit_code, stdout, stderr = self.runner.run_with_input([])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Usage:", stdout)

    def test_normal_message_processing(self):
        """Test program with normal message input"""
        message = "status_report_normal"
        auth_cmd = "test_auth\n"
        stdin_data = auth_cmd

        exit_code, stdout, stderr = self.runner.run_with_stdin([message], stdin_data)
        self.assertEqual(exit_code, 0)
        self.assertIn("Polaris Satellite Communication System", stdout)
        self.assertIn("Protected mode enabled", stdout)
        self.assertIn("Processing message with protection", stdout)
        self.assertIn("Message processed successfully:", stdout)

    def test_authentication_success(self):
        """Test successful authentication"""
        message = "test_message"
        auth_cmd = "AUTH_SUCCESS\n"

        exit_code, stdout, stderr = self.runner.run_with_stdin([message], auth_cmd)
        self.assertEqual(exit_code, 0)
        self.assertIn("Response sent to ground control!", stdout)

    def test_authentication_failure(self):
        """Test authentication failure"""
        message = "test_message"
        auth_cmd = "INVALID_AUTH\n"

        exit_code, stdout, stderr = self.runner.run_with_stdin([message], auth_cmd)
        self.assertEqual(exit_code, 0)
        self.assertIn("Authentication failed", stdout)
        self.assertNotIn("Response sent to ground control!", stdout)

    def test_empty_message_processing(self):
        """Test program with empty message"""
        message = ""
        auth_cmd = "test_auth\n"

        exit_code, stdout, stderr = self.runner.run_with_stdin([message], auth_cmd)
        self.assertEqual(exit_code, 0)
        self.assertIn("Message processed successfully:", stdout)

    def test_empty_authentication_command(self):
        """Test program with empty authentication command"""
        message = "test_message"
        auth_cmd = "\n"

        exit_code, stdout, stderr = self.runner.run_with_stdin([message], auth_cmd)
        self.assertEqual(exit_code, 0)
        self.assertIn("Authentication failed", stdout)

    def test_long_message_input(self):
        """Test program with long message input"""
        message = "verylongmessagetotestbufferhandlingandprocessingcapabilities"
        auth_cmd = "test_auth\n"

        exit_code, stdout, stderr = self.runner.run_with_stdin([message], auth_cmd)
        self.assertEqual(exit_code, 0)
        self.assertIn("Processing message with protection", stdout)

    def test_special_characters_in_message(self):
        """Test program with special characters in message"""
        message = "message@with#special$chars&symbols"
        auth_cmd = "test_auth\n"

        exit_code, stdout, stderr = self.runner.run_with_stdin([message], auth_cmd)
        self.assertEqual(exit_code, 0)
        self.assertIn("Message processed successfully:", stdout)

    def test_protection_mode_indicator(self):
        """Test that protection mode is indicated"""
        message = "test"
        auth_cmd = "test\n"

        exit_code, stdout, stderr = self.runner.run_with_stdin([message], auth_cmd)
        self.assertEqual(exit_code, 0)
        self.assertIn("Protected mode enabled", stdout)


if __name__ == '__main__':
    unittest.main()
