import unittest
import os
import tempfile
try:
    from .test_utils import ProgramRunner
except ImportError:
    from test_utils import ProgramRunner


class TestSpicaNavigationSystem(unittest.TestCase):
    """Unit tests for Spica satellite navigation system"""

    def setUp(self):
        """Set up test environment"""
        self.runner = ProgramRunner(os.path.join(os.path.dirname(__file__), '..', 'spica'))
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

    def tearDown(self):
        """Clean up test environment"""
        # Clean up any navigation.log files created during tests
        log_path = os.path.join(os.path.dirname(self.runner.program_path), 'navigation.log')
        if os.path.exists(log_path):
            os.remove(log_path)
        os.chdir(self.original_cwd)

    def test_program_exists(self):
        """Test that spica program exists and is executable"""
        self.assertTrue(os.path.exists(self.runner.program_path))

    def test_no_arguments_error(self):
        """Test program behavior with no arguments"""
        exit_code, stdout, stderr = self.runner.run_with_input([])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Usage:", stdout)

    def test_normal_navigation_data_input(self):
        """Test program with normal navigation data input"""
        nav_data = "coordinates:45.0,90.0,altitude:500"
        exit_code, stdout, stderr = self.runner.run_with_input([nav_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Spica Satellite Navigation System", stdout)
        self.assertIn("Processing navigation data", stdout)
        self.assertIn("Navigation log:", stdout)

    def test_trajectory_adjustment_trigger(self):
        """Test trajectory adjustment when input contains adjust keyword"""
        nav_data = "trajectory_adjust_coordinates:10.0,20.0"
        exit_code, stdout, stderr = self.runner.run_with_input([nav_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Trajectory adjusted successfully!", stdout)

    def test_no_trajectory_adjustment(self):
        """Test no trajectory adjustment when input lacks adjust keyword"""
        nav_data = "normal_coordinates:30.0,40.0"
        exit_code, stdout, stderr = self.runner.run_with_input([nav_data])
        self.assertEqual(exit_code, 0)
        self.assertNotIn("Trajectory adjusted successfully!", stdout)

    def test_navigation_log_creation(self):
        """Test that navigation log file is created"""
        nav_data = "test_navigation_data"
        log_path = os.path.join(os.path.dirname(self.runner.program_path), 'navigation.log')

        # Remove existing log if present
        if os.path.exists(log_path):
            os.remove(log_path)

        exit_code, stdout, stderr = self.runner.run_with_input([nav_data])
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(log_path))

        # Verify log content
        with open(log_path, 'r') as f:
            content = f.read()
            self.assertIn("Log entry:", content)

    def test_empty_navigation_data(self):
        """Test program with empty navigation data"""
        exit_code, stdout, stderr = self.runner.run_with_input([""])
        self.assertEqual(exit_code, 0)
        self.assertIn("Navigation log:", stdout)

    def test_special_characters_in_navigation_data(self):
        """Test program with special characters in navigation data"""
        nav_data = "data:with@special#chars&symbols"
        exit_code, stdout, stderr = self.runner.run_with_input([nav_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Navigation log:", stdout)

    def test_long_navigation_data_processing(self):
        """Test program with long navigation data"""
        nav_data = "verylongnavigationdatatestingbufferboundariesandprocessingcapabilities"
        exit_code, stdout, stderr = self.runner.run_with_input([nav_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Navigation log:", stdout)


if __name__ == '__main__':
    unittest.main()
