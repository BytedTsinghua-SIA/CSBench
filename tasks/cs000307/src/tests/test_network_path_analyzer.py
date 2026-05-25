import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class TestNetworkPathAnalyzer(unittest.TestCase):
    """Unit tests for NetworkPathAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_ping_data = """[1640995200.123456] icmp_seq=1 ttl=64 time=12.34 ms
[1640995200.323456] icmp_seq=2 ttl=64 time=11.56 ms
[1640995200.523456] icmp_seq=3 ttl=64 time=15.78 ms
"""

    def test_analyzer_initializes_with_valid_ping_file(self):
        """Test that analyzer initializes correctly with a valid ping file."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_ping_data)
            temp_file = f.name

        try:
            from network_path_analyzer import NetworkPathAnalyzer

            analyzer = NetworkPathAnalyzer(temp_file)

            self.assertEqual(analyzer.ping_file, temp_file)
            self.assertIsNotNone(analyzer.parser)
            self.assertIsNotNone(analyzer.data)

        finally:
            os.unlink(temp_file)

    def test_analyzer_extracts_target_host_from_filename(self):
        """Test target host extraction from ping filename."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False,
                                       prefix='ping_google_') as f:
            f.write(self.sample_ping_data)
            temp_file = f.name

        try:
            from network_path_analyzer import NetworkPathAnalyzer

            analyzer = NetworkPathAnalyzer(temp_file)

            # Should extract 'google' from filename
            self.assertIn('google', analyzer.target_host)

        finally:
            os.unlink(temp_file)

    @patch('network_path_analyzer.Path')
    def test_analyzer_creates_output_directory(self, mock_path):
        """Test that analyzer creates output directory."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.mkdir = MagicMock()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_ping_data)
            temp_file = f.name

        try:
            from network_path_analyzer import NetworkPathAnalyzer

            analyzer = NetworkPathAnalyzer(temp_file, output_dir="test_output")

            # Should call mkdir on the output directory
            mock_path_instance.mkdir.assert_called_once_with(exist_ok=True)

        finally:
            os.unlink(temp_file)

    def test_analyzer_handles_missing_ping_file(self):
        """Test that analyzer handles missing ping file gracefully."""
        from network_path_analyzer import NetworkPathAnalyzer

        with self.assertRaises(FileNotFoundError):
            NetworkPathAnalyzer("nonexistent_file.txt")

    @patch('network_path_analyzer.Path')
    def test_analyzer_initializes_all_components(self, mock_path):
        """Test that analyzer initializes all required components."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_ping_data)
            temp_file = f.name

        try:
            from network_path_analyzer import NetworkPathAnalyzer

            analyzer = NetworkPathAnalyzer(temp_file)

            # Check that all analyzers are initialized
            self.assertIsNotNone(analyzer.delivery_stats)
            self.assertIsNotNone(analyzer.path_analyzer)
            self.assertIsNotNone(analyzer.loss_analyzer)
            self.assertIsNotNone(analyzer.rtt_analyzer)

        finally:
            os.unlink(temp_file)

    def test_run_complete_analysis_calls_components(self):
        """Test that complete analysis calls all component methods."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_ping_data)
            temp_file = f.name

        try:
            from network_path_analyzer import NetworkPathAnalyzer

            analyzer = NetworkPathAnalyzer(temp_file)

            # Mock the plotting methods to avoid file I/O
            analyzer.rtt_analyzer.plot_rtt_time_series = MagicMock()
            analyzer.rtt_analyzer.plot_rtt_cdf = MagicMock()
            analyzer.rtt_analyzer.plot_rtt_correlation = MagicMock()

            # Mock throughput analyzer methods to avoid ping command execution
            with patch('network_path_analyzer.ThroughputAnalyzer') as mock_throughput_class:
                mock_throughput_instance = MagicMock()
                mock_throughput_class.return_value = mock_throughput_instance
                mock_throughput_instance.run_throughput_experiment.return_value = []
                mock_throughput_instance.plot_throughput_results = MagicMock()

                # This should not raise an exception
                analyzer.run_complete_analysis()

                # Verify that plotting methods were called
                analyzer.rtt_analyzer.plot_rtt_time_series.assert_called_once()
                analyzer.rtt_analyzer.plot_rtt_cdf.assert_called_once()
                analyzer.rtt_analyzer.plot_rtt_correlation.assert_called_once()

                # Verify that throughput methods were called
                mock_throughput_class.assert_called_once_with(analyzer.target_host)
                mock_throughput_instance.run_throughput_experiment.assert_called_once()
                mock_throughput_instance.plot_throughput_results.assert_called_once()

        finally:
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()
