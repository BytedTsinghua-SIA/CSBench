import unittest
import os
try:
    from .test_utils import ProgramRunner
except ImportError:
    from test_utils import ProgramRunner


class TestRemusSatelliteControl(unittest.TestCase):
    """Unit tests for Remus satellite control system"""

    def setUp(self):
        """Set up test environment"""
        self.runner = ProgramRunner(os.path.join(os.path.dirname(__file__), '..', 'remus'))

    def test_program_exists(self):
        """Test that remus program exists and is executable"""
        self.assertTrue(os.path.exists(self.runner.program_path))

    def test_no_arguments_error(self):
        """Test program behavior with no arguments"""
        exit_code, stdout, stderr = self.runner.run_with_input([])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Usage:", stdout)

    def test_normal_username_input(self):
        """Test program with normal username input"""
        username = "testuser"
        exit_code, stdout, stderr = self.runner.run_with_input([username])
        self.assertEqual(exit_code, 0)
        self.assertIn("Remus Satellite Control System", stdout)
        self.assertIn("Initializing authentication", stdout)
        self.assertIn(f"Welcome to Remus satellite control, {username}!", stdout)

    def test_admin_user_launch_access(self):
        """Test admin user has launch privileges"""
        exit_code, stdout, stderr = self.runner.run_with_input(["admin"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Satellite launched successfully!", stdout)

    def test_non_admin_user_denied_access(self):
        """Test non-admin user is denied launch access"""
        username = "regularuser"
        exit_code, stdout, stderr = self.runner.run_with_input([username])
        self.assertEqual(exit_code, 0)
        self.assertIn("Access denied", stdout)
        self.assertNotIn("Satellite launched successfully!", stdout)

    def test_empty_username_handling(self):
        """Test program behavior with empty username"""
        exit_code, stdout, stderr = self.runner.run_with_input([""])
        self.assertEqual(exit_code, 0)
        self.assertIn("Welcome to Remus satellite control, !", stdout)
        self.assertIn("Access denied", stdout)

    def test_special_characters_in_username(self):
        """Test program with special characters in username"""
        username = "user@domain.com"
        exit_code, stdout, stderr = self.runner.run_with_input([username])
        self.assertEqual(exit_code, 0)
        self.assertIn(f"Welcome to Remus satellite control, {username}!", stdout)
        self.assertIn("Access denied", stdout)



if __name__ == '__main__':
    unittest.main()
