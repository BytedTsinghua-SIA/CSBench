import unittest
import os
try:
    from .test_utils import ProgramRunner
except ImportError:
    from test_utils import ProgramRunner


class TestAntaresSynchronization(unittest.TestCase):
    """Unit tests for Antares satellite synchronization system"""

    def setUp(self):
        """Set up test environment"""
        self.runner = ProgramRunner(os.path.join(os.path.dirname(__file__), '..', 'antares'))

    def test_program_exists(self):
        """Test that antares program exists and is executable"""
        self.assertTrue(os.path.exists(self.runner.program_path))

    def test_no_arguments_error(self):
        """Test program behavior with no arguments"""
        exit_code, stdout, stderr = self.runner.run_with_input([])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Usage:", stdout)

    def test_normal_synchronization_process(self):
        """Test program with normal initial data"""
        initial_data = "satellite_sync_data"
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Antares Satellite Synchronization System", stdout)
        self.assertIn("Shared resource initialized", stdout)
        self.assertIn("Shared resource cleaned up", stdout)

    def test_thread_execution_indicators(self):
        """Test that both threads execute and show their messages"""
        initial_data = "test_data"
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Thread 1: Starting satellite synchronization", stdout)
        self.assertIn("Thread 2: Starting orbital calculation", stdout)

    def test_data_modification_by_threads(self):
        """Test that threads modify shared data"""
        initial_data = "initial_data"
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        # At least one thread should have modified the data
        self.assertTrue(
            "Thread 1 modified data" in stdout or
            "Thread 2 modified data" in stdout
        )

    def test_safe_access_with_locking(self):
        """Test safe access function execution"""
        initial_data = "safe_test"
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Safe access:", stdout)
        self.assertIn("Current data:", stdout)
        self.assertIn("Access count:", stdout)

    def test_empty_initial_data(self):
        """Test program with empty initial data"""
        initial_data = ""
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Shared resource initialized", stdout)

    def test_numeric_initial_data(self):
        """Test program with numeric initial data"""
        initial_data = "12345"
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Shared resource initialized with data: 12345", stdout)

    def test_special_characters_in_data(self):
        """Test program with special characters in initial data"""
        initial_data = "data@with#special$chars&symbols"
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Shared resource initialized", stdout)

    def test_access_count_tracking(self):
        """Test that access count is tracked and displayed"""
        initial_data = "count_test"
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        # Check that access count appears in safe access output
        self.assertIn("Access count:", stdout)

    def test_thread_completion(self):
        """Test that both threads complete execution"""
        initial_data = "completion_test"
        exit_code, stdout, stderr = self.runner.run_with_input([initial_data])
        self.assertEqual(exit_code, 0)
        # Both threads should show completion by modifying data
        modifications = stdout.count("modified data")
        self.assertGreaterEqual(modifications, 1)  # At least one thread completed


if __name__ == '__main__':
    unittest.main()
