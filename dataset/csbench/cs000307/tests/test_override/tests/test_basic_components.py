import unittest
from unittest.mock import patch, MagicMock, mock_open


class TestBasicComponents(unittest.TestCase):
    """Unit tests for basic components that don't require external dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_traceroute_data = """traceroute to example.com (93.184.216.34), 64 hops max, 52 byte packets
 1  router.local (192.168.1.1)  1.234 ms  1.567 ms  1.890 ms
 2  isp-gateway (10.0.0.1)  5.678 ms  5.901 ms  6.123 ms
"""

    def test_path_analyzer_initialization(self):
        """Test that PathAnalyzer initializes correctly."""
        from network_path_analyzer import PathAnalyzer

        analyzer = PathAnalyzer()

        self.assertIsInstance(analyzer.path_info, list)
        self.assertEqual(len(analyzer.path_info), 0)
        self.assertIsNone(analyzer.traceroute_file)

    def test_path_analyzer_with_file(self):
        """Test PathAnalyzer with a traceroute file."""
        from network_path_analyzer import PathAnalyzer
        from unittest.mock import mock_open

        with patch('builtins.open', mock_open(read_data=self.sample_traceroute_data)):
            analyzer = PathAnalyzer("dummy_traceroute.txt")

        self.assertIsNotNone(analyzer.traceroute_file)
        self.assertGreater(len(analyzer.path_info), 0)

    def test_path_analyzer_geographic_analysis(self):
        """Test geographic path analysis returns a string."""
        from network_path_analyzer import PathAnalyzer

        analyzer = PathAnalyzer()
        result = analyzer.analyze_geographic_path()

        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_throughput_analyzer_initialization(self):
        """Test ThroughputAnalyzer initializes correctly."""
        from network_path_analyzer import ThroughputAnalyzer

        target = "example.com"
        analyzer = ThroughputAnalyzer(target)

        self.assertEqual(analyzer.target_host, target)

    def test_throughput_analyzer_parse_ping_summary(self):
        """Test ping summary parsing."""
        from network_path_analyzer import ThroughputAnalyzer

        analyzer = ThroughputAnalyzer("example.com")

        ping_output = """PING example.com (93.184.216.34): 56 data bytes
64 bytes from 93.184.216.34: icmp_seq=0 ttl=64 time=12.3 ms

--- example.com ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
"""

        sent, received, loss_rate = analyzer._parse_ping_summary(ping_output)

        self.assertEqual(sent, 1)
        self.assertEqual(received, 1)
        self.assertEqual(loss_rate, 0.0)

    def test_throughput_analyzer_parse_malformed_output(self):
        """Test parsing of malformed ping output."""
        from network_path_analyzer import ThroughputAnalyzer

        analyzer = ThroughputAnalyzer("example.com")

        ping_output = "Some random output"

        sent, received, loss_rate = analyzer._parse_ping_summary(ping_output)

        self.assertEqual(sent, 0)
        self.assertEqual(received, 0)
        self.assertEqual(loss_rate, 1.0)

    def test_main_analyzer_target_extraction(self):
        """Test target host extraction from filename."""
        from network_path_analyzer import NetworkPathAnalyzer
        from pathlib import Path

        # Mock the file operations and dependencies
        sample_data = """[1640995200.123456] icmp_seq=1 ttl=64 time=12.34 ms
[1640995200.323456] icmp_seq=2 ttl=64 time=11.56 ms"""

        with patch('network_path_analyzer.Path') as mock_path, \
             patch('builtins.open', mock_open(read_data=sample_data)):

            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance
            mock_path_instance.mkdir = MagicMock()
            mock_path_instance.name = "ping_google_test.txt"

            analyzer = NetworkPathAnalyzer("ping_google_test.txt")

            # Should extract 'google' from filename
            self.assertIn('google', analyzer.target_host)

    def test_main_analyzer_missing_file_handling(self):
        """Test handling of missing ping file."""
        from network_path_analyzer import NetworkPathAnalyzer

        with self.assertRaises(FileNotFoundError):
            NetworkPathAnalyzer("nonexistent_file.txt")


if __name__ == '__main__':
    unittest.main()
