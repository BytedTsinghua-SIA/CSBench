import unittest
import os
try:
    from .test_utils import ProgramRunner
except ImportError:
    from test_utils import ProgramRunner


class TestRigelAdvancedControl(unittest.TestCase):
    """Unit tests for Rigel advanced satellite control system"""

    def setUp(self):
        """Set up test environment"""
        self.runner = ProgramRunner(os.path.join(os.path.dirname(__file__), '..', 'rigel'))

    def test_program_exists(self):
        """Test that rigel program exists and is executable"""
        self.assertTrue(os.path.exists(self.runner.program_path))

    def test_insufficient_arguments_error(self):
        """Test program behavior with insufficient arguments"""
        exit_code, stdout, stderr = self.runner.run_with_input([])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Usage:", stdout)
        self.assertIn("Rigel Advanced Satellite Control System", stdout)

    def test_normal_command_processing(self):
        """Test program with normal command and data"""
        command = "test_command"
        data = "test_data"
        exit_code, stdout, stderr = self.runner.run_with_input([command, data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Rigel Advanced Satellite Control System", stdout)
        self.assertIn("Processing advanced satellite command", stdout)
        self.assertIn("Command processing complete", stdout)

    def test_chunk_creation_and_execution(self):
        """Test advanced chunk creation and callback execution"""
        command = "chunk_test"
        data = "chunk_data"
        exit_code, stdout, stderr = self.runner.run_with_input([command, data])
        self.assertEqual(exit_code, 0)
        # Chunk is created but callback is NULL, so no execution
        self.assertNotIn("Executing chunk callback", stdout)

    def test_gadget_address_display(self):
        """Test that ROP gadget addresses are displayed"""
        command = "gadget_test"
        data = "gadget_data"
        exit_code, stdout, stderr = self.runner.run_with_input([command, data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Available ROP gadgets:", stdout)
        self.assertIn("gadget1:", stdout)
        self.assertIn("gadget2:", stdout)
        self.assertIn("gadget3:", stdout)
        self.assertIn("secret_function:", stdout)

    def test_format_string_with_three_args(self):
        """Test program with format string argument"""
        command = "format_test"
        data = "format_data"
        format_str = "Data: %s"
        exit_code, stdout, stderr = self.runner.run_with_input([command, data, format_str])
        self.assertEqual(exit_code, 0)
        self.assertIn("Advanced log:", stdout)


    def test_empty_command_handling(self):
        """Test program with empty command"""
        command = ""
        data = "test_data"
        exit_code, stdout, stderr = self.runner.run_with_input([command, data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Processing advanced satellite command", stdout)

    def test_empty_data_handling(self):
        """Test program with empty data"""
        command = "test_command"
        data = ""
        exit_code, stdout, stderr = self.runner.run_with_input([command, data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Command processing complete", stdout)

    def test_special_characters_in_command(self):
        """Test program with special characters in command"""
        command = "command@with#special$chars"
        data = "normal_data"
        exit_code, stdout, stderr = self.runner.run_with_input([command, data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Processing advanced satellite command", stdout)

    def test_special_characters_in_data(self):
        """Test program with special characters in data"""
        command = "normal_command"
        data = "data@with#special$chars&symbols"
        exit_code, stdout, stderr = self.runner.run_with_input([command, data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Available ROP gadgets:", stdout)

    def test_security_features_initialization(self):
        """Test that advanced security features are mentioned"""
        command = "security_test"
        data = "security_data"
        exit_code, stdout, stderr = self.runner.run_with_input([command, data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Initializing advanced security features", stdout)


if __name__ == '__main__':
    unittest.main()
