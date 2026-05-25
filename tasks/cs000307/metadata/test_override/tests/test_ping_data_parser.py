import unittest
from unittest.mock import mock_open, patch

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class TestPingDataParser(unittest.TestCase):
    """Unit tests for PingDataParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_ping_data = """[1640995200.123456] icmp_seq=1 ttl=64 time=12.34 ms
[1640995200.323456] icmp_seq=2 ttl=64 time=11.56 ms
[1640995200.523456] icmp_seq=3 ttl=64 time=15.78 ms
"""

    @patch('builtins.open', new_callable=mock_open)
    def test_parser_initializes_with_valid_file(self, mock_file):
        """Test that parser initializes correctly with a valid file."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        mock_file.return_value.read.return_value = self.sample_ping_data

        from network_path_analyzer import PingDataParser

        parser = PingDataParser("dummy_file.txt")

        self.assertIsInstance(parser.data, pd.DataFrame)
        self.assertIn('timestamp', parser.data.columns)
        self.assertIn('sequence', parser.data.columns)
        self.assertIn('rtt', parser.data.columns)
        self.assertIn('received', parser.data.columns)

    def test_parser_handles_empty_file(self):
        """Test that parser handles empty input file gracefully."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import PingDataParser
        from unittest.mock import mock_open

        with patch('builtins.open', mock_open(read_data="")):
            parser = PingDataParser("empty_file.txt")

        self.assertIsInstance(parser.data, pd.DataFrame)

    def test_parser_extracts_correct_sequence_numbers(self):
        """Test that parser correctly extracts sequence numbers."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import PingDataParser
        from unittest.mock import mock_open

        with patch('builtins.open', mock_open(read_data=self.sample_ping_data)):
            parser = PingDataParser("dummy_file.txt")

        expected_sequences = [1, 2, 3]
        actual_sequences = parser.data['sequence'].tolist()

        self.assertEqual(actual_sequences, expected_sequences)

    def test_parser_extracts_rtt_values(self):
        """Test that parser correctly extracts RTT values."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import PingDataParser
        from unittest.mock import mock_open

        with patch('builtins.open', mock_open(read_data=self.sample_ping_data)):
            parser = PingDataParser("dummy_file.txt")

        expected_rtts = [12.34, 11.56, 15.78]
        actual_rtts = parser.data['rtt'].tolist()

        self.assertEqual(actual_rtts, expected_rtts)

    def test_parser_marks_all_packets_as_received(self):
        """Test that parser marks all parsed packets as received."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import PingDataParser
        from unittest.mock import mock_open

        with patch('builtins.open', mock_open(read_data=self.sample_ping_data)):
            parser = PingDataParser("dummy_file.txt")

        received_values = parser.data['received'].tolist()
        self.assertTrue(all(received_values))


if __name__ == '__main__':
    unittest.main()
