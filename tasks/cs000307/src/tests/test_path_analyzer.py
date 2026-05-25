import unittest
from unittest.mock import mock_open, patch


class TestPathAnalyzer(unittest.TestCase):
    """Unit tests for PathAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_traceroute_data = """traceroute to example.com (93.184.216.34), 64 hops max, 52 byte packets
 1  router.local (192.168.1.1)  1.234 ms  1.567 ms  1.890 ms
 2  isp-gateway (10.0.0.1)  5.678 ms  5.901 ms  6.123 ms
 3  backbone-router (203.0.113.1)  12.345 ms  12.678 ms  13.001 ms
"""

    def test_analyzer_initializes_without_file(self):
        """Test that analyzer initializes correctly without a traceroute file."""
        from network_path_analyzer import PathAnalyzer

        analyzer = PathAnalyzer()

        self.assertIsInstance(analyzer.path_info, list)
        self.assertEqual(len(analyzer.path_info), 0)

    def test_analyzer_parses_traceroute_data(self):
        """Test that analyzer correctly parses traceroute output."""
        from network_path_analyzer import PathAnalyzer
        from unittest.mock import mock_open

        with patch('builtins.open', mock_open(read_data=self.sample_traceroute_data)):
            analyzer = PathAnalyzer("dummy_traceroute.txt")

        self.assertGreater(len(analyzer.path_info), 0)

        # Check first hop
        first_hop = analyzer.path_info[0]
        self.assertEqual(first_hop['hop'], 1)
        self.assertIn('192.168.1.1', first_hop['ips'])

    def test_analyze_geographic_path_returns_string(self):
        """Test that geographic analysis returns a string."""
        from network_path_analyzer import PathAnalyzer

        analyzer = PathAnalyzer()
        result = analyzer.analyze_geographic_path()

        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_analyzer_handles_malformed_lines(self):
        """Test that analyzer handles malformed traceroute lines gracefully."""
        from network_path_analyzer import PathAnalyzer
        from unittest.mock import mock_open

        malformed_data = """traceroute to example.com (93.184.216.34), 64 hops max, 52 byte packets
malformed line without numbers
 1  router.local (192.168.1.1)  1.234 ms  1.567 ms  1.890 ms
another malformed line
"""

        with patch('builtins.open', mock_open(read_data=malformed_data)):
            analyzer = PathAnalyzer("dummy_traceroute.txt")

        # Should still parse the valid line
        self.assertGreater(len(analyzer.path_info), 0)
        self.assertEqual(analyzer.path_info[0]['hop'], 1)

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_analyzer_handles_missing_file(self, mock_file):
        """Test that analyzer handles missing traceroute file gracefully."""
        from network_path_analyzer import PathAnalyzer

        # Should not raise exception
        analyzer = PathAnalyzer("nonexistent_file.txt")

        self.assertIsInstance(analyzer.path_info, list)
        self.assertEqual(len(analyzer.path_info), 0)


if __name__ == '__main__':
    unittest.main()
