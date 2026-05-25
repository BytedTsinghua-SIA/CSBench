import unittest
import os
try:
    from .test_utils import ProgramRunner
except ImportError:
    from test_utils import ProgramRunner


class TestVegaDataStorage(unittest.TestCase):
    """Unit tests for Vega satellite data storage system"""

    def setUp(self):
        """Set up test environment"""
        self.runner = ProgramRunner(os.path.join(os.path.dirname(__file__), '..', 'vega'))

    def test_program_exists(self):
        """Test that vega program exists and is executable"""
        self.assertTrue(os.path.exists(self.runner.program_path))

    def test_no_arguments_error(self):
        """Test program behavior with no arguments"""
        exit_code, stdout, stderr = self.runner.run_with_input([])
        self.assertNotEqual(exit_code, 0)
        self.assertIn("Usage:", stdout)

    def test_normal_satellite_data_storage(self):
        """Test program with normal satellite data input"""
        data = "satellite_telemetry_data"
        exit_code, stdout, stderr = self.runner.run_with_input([data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Vega Satellite Data Storage System", stdout)
        self.assertIn("Storing satellite data", stdout)
        self.assertIn("Data stored successfully", stdout)
        self.assertIn("Processing stored data:", stdout)

    def test_empty_data_storage(self):
        """Test program with empty satellite data"""
        data = ""
        exit_code, stdout, stderr = self.runner.run_with_input([data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Data stored successfully", stdout)
        self.assertIn("Processing stored data:", stdout)

    def test_small_data_processing(self):
        """Test program with small data input"""
        data = "abc"
        exit_code, stdout, stderr = self.runner.run_with_input([data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Processing stored data: abc", stdout)

    def test_special_characters_in_data(self):
        """Test program with special characters in satellite data"""
        data = "data@with#special$chars&symbols"
        exit_code, stdout, stderr = self.runner.run_with_input([data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Storing satellite data", stdout)
        self.assertIn("Data stored successfully", stdout)

    def test_numeric_data_storage(self):
        """Test program with numeric satellite data"""
        data = "1234567890"
        exit_code, stdout, stderr = self.runner.run_with_input([data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Processing stored data: 1234567890", stdout)

    def test_data_cleanup_message(self):
        """Test that data cleanup message is displayed"""
        data = "test_data"
        exit_code, stdout, stderr = self.runner.run_with_input([data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Satellite data freed", stdout)

    def test_data_processing_after_storage(self):
        """Test that data is processed after storage"""
        data = "telemetry_info"
        exit_code, stdout, stderr = self.runner.run_with_input([data])
        self.assertEqual(exit_code, 0)
        # Ensure processing happens after storage
        storage_pos = stdout.find("Data stored successfully")
        processing_pos = stdout.find("Processing stored data:")
        self.assertTrue(storage_pos < processing_pos)

    def test_long_data_input_processing(self):
        """Test program with long data input"""
        data = "verylongsatellitedataforheapstorageandprocessingtestingpurposes"
        exit_code, stdout, stderr = self.runner.run_with_input([data])
        self.assertEqual(exit_code, 0)
        self.assertIn("Storing satellite data", stdout)


if __name__ == '__main__':
    unittest.main()
