import unittest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any


class TestThroughputAnalyzer(unittest.TestCase):
    """Unit tests for ThroughputAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.target_host = "example.com"

    def test_analyzer_initializes_with_target_host(self):
        """Test that analyzer initializes correctly with a target host."""
        from network_path_analyzer import ThroughputAnalyzer

        analyzer = ThroughputAnalyzer(self.target_host)

        self.assertEqual(analyzer.target_host, self.target_host)

    @patch('subprocess.run')
    def test_run_throughput_experiment_returns_list(self, mock_subprocess):
        """Test that throughput experiment returns a list of results."""
        # Mock subprocess to simulate ping output
        mock_result = MagicMock()
        mock_result.stdout = """PING example.com (93.184.216.34): 56 data bytes
64 bytes from 93.184.216.34: icmp_seq=0 ttl=64 time=12.3 ms
64 bytes from 93.184.216.34: icmp_seq=1 ttl=64 time=11.8 ms

--- example.com ping statistics ---
2 packets transmitted, 2 packets received, 0.0% packet loss
"""
        mock_subprocess.return_value = mock_result

        from network_path_analyzer import ThroughputAnalyzer

        analyzer = ThroughputAnalyzer(self.target_host)
        results = analyzer.run_throughput_experiment(duration=1)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_run_throughput_experiment_result_structure(self):
        """Test that experiment results have the correct structure."""
        with patch('subprocess.run') as mock_subprocess:
            mock_result = MagicMock()
            mock_result.stdout = """PING example.com (93.184.216.34): 56 data bytes
64 bytes from 93.184.216.34: icmp_seq=0 ttl=64 time=12.3 ms

--- example.com ping statistics ---
1 packets transmitted, 1 packets received, 0.0% packet loss
"""
            mock_subprocess.return_value = mock_result

            from network_path_analyzer import ThroughputAnalyzer

            analyzer = ThroughputAnalyzer(self.target_host)
            results = analyzer.run_throughput_experiment(duration=1)

            # Check structure of first result
            result = results[0]
            expected_keys = [
                'packet_size', 'interval', 'sent', 'received', 'loss_rate',
                'request_data_rate_bps', 'reply_data_rate_bps'
            ]

            for key in expected_keys:
                self.assertIn(key, result)

    @patch('subprocess.run')
    def test_run_throughput_experiment_handles_timeout(self, mock_subprocess):
        """Test that experiment handles subprocess timeouts gracefully."""
        import subprocess
        mock_subprocess.side_effect = subprocess.TimeoutExpired("ping", 6)

        from network_path_analyzer import ThroughputAnalyzer

        analyzer = ThroughputAnalyzer(self.target_host)
        results = analyzer.run_throughput_experiment(duration=1)

        # Should still return results, but with zero values
        self.assertIsInstance(results, list)
        result = results[0]
        self.assertEqual(result['sent'], 0)
        self.assertEqual(result['received'], 0)

    def test_parse_ping_summary_extracts_statistics(self):
        """Test parsing of ping command summary."""
        from network_path_analyzer import ThroughputAnalyzer

        analyzer = ThroughputAnalyzer(self.target_host)

        ping_output = """PING example.com (93.184.216.34): 56 data bytes
64 bytes from 93.184.216.34: icmp_seq=0 ttl=64 time=12.3 ms
64 bytes from 93.184.216.34: icmp_seq=1 ttl=64 time=11.8 ms

--- example.com ping statistics ---
5 packets transmitted, 4 packets received, 20.0% packet loss
"""

        sent, received, loss_rate = analyzer._parse_ping_summary(ping_output)

        self.assertEqual(sent, 5)
        self.assertEqual(received, 4)
        self.assertAlmostEqual(loss_rate, 0.2)

    def test_parse_ping_summary_handles_no_packets(self):
        """Test parsing when no packets are sent/received."""
        from network_path_analyzer import ThroughputAnalyzer

        analyzer = ThroughputAnalyzer(self.target_host)

        ping_output = "No statistics available"

        sent, received, loss_rate = analyzer._parse_ping_summary(ping_output)

        self.assertEqual(sent, 0)
        self.assertEqual(received, 0)
        self.assertEqual(loss_rate, 1.0)

    def test_parse_ping_summary_handles_malformed_output(self):
        """Test parsing of malformed ping output."""
        from network_path_analyzer import ThroughputAnalyzer

        analyzer = ThroughputAnalyzer(self.target_host)

        ping_output = "Some random output without statistics"

        sent, received, loss_rate = analyzer._parse_ping_summary(ping_output)

        self.assertEqual(sent, 0)
        self.assertEqual(received, 0)
        self.assertEqual(loss_rate, 1.0)


if __name__ == '__main__':
    unittest.main()
