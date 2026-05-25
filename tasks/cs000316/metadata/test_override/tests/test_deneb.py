import unittest
import os
try:
    from .test_utils import ProgramRunner
except ImportError:
    from test_utils import ProgramRunner


class TestDenebTelemetrySystem(unittest.TestCase):
    """Unit tests for Deneb satellite telemetry system"""

    def setUp(self):
        """Set up test environment"""
        self.runner = ProgramRunner(os.path.join(os.path.dirname(__file__), '..', 'deneb'))

    def test_program_exists(self):
        """Test that deneb program exists and is executable"""
        self.assertTrue(os.path.exists(self.runner.program_path))

    def test_no_arguments_error(self):
        """Test program behavior with no arguments"""
        exit_code, stdout, stderr = self.runner.run_with_input([])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Usage:", stdout)

    def test_normal_telemetry_data_storage(self):
        """Test program with normal telemetry data input"""
        telemetry_data = "satellite_telemetry_readings"
        exit_code, stdout, stderr = self.runner.run_with_input([telemetry_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Deneb Satellite Telemetry System", stdout)
        self.assertIn("Telemetry buffer allocated", stdout)
        self.assertIn("Telemetry data stored:", stdout)
        self.assertIn("Telemetry buffer freed", stdout)

    def test_empty_telemetry_data(self):
        """Test program with empty telemetry data"""
        telemetry_data = ""
        exit_code, stdout, stderr = self.runner.run_with_input([telemetry_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Telemetry buffer allocated", stdout)
        self.assertIn("Telemetry data stored:", stdout)

    def test_telemetry_processing_sequence(self):
        """Test the complete telemetry processing sequence"""
        telemetry_data = "test_data"
        exit_code, stdout, stderr = self.runner.run_with_input([telemetry_data])
        self.assertEqual(exit_code, 0)

        # Check sequence: allocate -> store -> free -> process -> reallocate -> process
        self.assertIn("Telemetry buffer allocated", stdout)
        self.assertIn("Telemetry data stored: test_data", stdout)
        self.assertIn("Telemetry buffer freed", stdout)
        self.assertIn("No telemetry data to process", stdout)

    def test_new_telemetry_allocation(self):
        """Test new telemetry allocation after free"""
        telemetry_data = "initial_data"
        exit_code, stdout, stderr = self.runner.run_with_input([telemetry_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("New telemetry allocated:", stdout)

    def test_short_data_acceptance(self):
        """Test that short telemetry data is accepted"""
        telemetry_data = "abc"
        exit_code, stdout, stderr = self.runner.run_with_input([telemetry_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Telemetry data stored: abc", stdout)

    def test_numeric_telemetry_data(self):
        """Test program with numeric telemetry data"""
        telemetry_data = "123456789"
        exit_code, stdout, stderr = self.runner.run_with_input([telemetry_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Telemetry data stored: 123456789", stdout)

    def test_special_characters_in_telemetry(self):
        """Test program with special characters in telemetry data"""
        telemetry_data = "telemetry@data#with$special&chars"
        exit_code, stdout, stderr = self.runner.run_with_input([telemetry_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Telemetry buffer allocated", stdout)

    def test_long_data_boundary_check(self):
        """Test program behavior near buffer size limits"""
        # Test data that's close to but under the 64 character limit
        telemetry_data = "x" * 63
        exit_code, stdout, stderr = self.runner.run_with_input([telemetry_data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Telemetry data stored:", stdout)


if __name__ == '__main__':
    unittest.main()
