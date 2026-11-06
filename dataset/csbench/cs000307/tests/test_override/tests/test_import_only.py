import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestImportOnly(unittest.TestCase):
    """Test that modules can be imported without errors."""

    def test_network_path_analyzer_import(self):
        """Test that the main module can be imported."""
        try:
            import network_path_analyzer
            # Check that basic classes are available
            self.assertTrue(hasattr(network_path_analyzer, 'PingDataParser'))
            self.assertTrue(hasattr(network_path_analyzer, 'DeliveryStatistics'))
            self.assertTrue(hasattr(network_path_analyzer, 'PathAnalyzer'))
            self.assertTrue(hasattr(network_path_analyzer, 'LossCorrelationAnalyzer'))
            self.assertTrue(hasattr(network_path_analyzer, 'RTTAnalyzer'))
            self.assertTrue(hasattr(network_path_analyzer, 'ThroughputAnalyzer'))
            self.assertTrue(hasattr(network_path_analyzer, 'NetworkPathAnalyzer'))
        except ImportError as e:
            self.fail(f"Failed to import network_path_analyzer: {e}")

    def test_dependency_flags(self):
        """Test that dependency flags are properly set."""
        import network_path_analyzer

        # Check that dependency flags exist
        self.assertTrue(hasattr(network_path_analyzer, 'HAS_PANDAS'))
        self.assertTrue(hasattr(network_path_analyzer, 'HAS_NUMPY'))
        self.assertTrue(hasattr(network_path_analyzer, 'HAS_MATPLOTLIB'))

        # Flags should be boolean
        self.assertIsInstance(network_path_analyzer.HAS_PANDAS, bool)
        self.assertIsInstance(network_path_analyzer.HAS_NUMPY, bool)
        self.assertIsInstance(network_path_analyzer.HAS_MATPLOTLIB, bool)


if __name__ == '__main__':
    unittest.main()
