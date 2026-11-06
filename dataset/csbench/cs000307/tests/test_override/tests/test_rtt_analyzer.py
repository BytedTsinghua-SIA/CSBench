import unittest

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class TestRTTAnalyzer(unittest.TestCase):
    """Unit tests for RTTAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample data with varying RTT values
        timestamps = pd.date_range('2023-01-01', periods=10, freq='200ms')
        rtt_values = [10.5, 12.3, 8.9, 15.7, 11.2, 9.8, 13.4, 7.6, 14.1, 10.9]
        received_values = [True] * 10

        self.sample_data = pd.DataFrame({
            'timestamp': timestamps,
            'sequence': list(range(1, 11)),
            'rtt': rtt_values,
            'received': received_values
        })

    def test_get_min_rtt(self):
        """Test calculation of minimum RTT."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import RTTAnalyzer

        analyzer = RTTAnalyzer(self.sample_data)
        min_rtt = analyzer.get_min_rtt()

        self.assertEqual(min_rtt, 7.6)

    def test_get_max_rtt(self):
        """Test calculation of maximum RTT."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import RTTAnalyzer

        analyzer = RTTAnalyzer(self.sample_data)
        max_rtt = analyzer.get_max_rtt()

        self.assertEqual(max_rtt, 15.7)

    def test_rtt_data_extraction_filters_received_packets(self):
        """Test that RTT data extraction only includes received packets."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import RTTAnalyzer

        # Create data with some lost packets
        mixed_data = self.sample_data.copy()
        mixed_data.loc[5, 'received'] = False  # Mark one packet as lost
        mixed_data.loc[5, 'rtt'] = None

        analyzer = RTTAnalyzer(mixed_data)

        # Should have 9 RTT values (one packet lost)
        self.assertEqual(len(analyzer.rtt_data), 9)

    def test_empty_rtt_data_handling(self):
        """Test behavior when no RTT data is available."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import RTTAnalyzer

        # Create data with all packets lost
        empty_rtt_data = self.sample_data.copy()
        empty_rtt_data['received'] = False
        empty_rtt_data['rtt'] = None

        analyzer = RTTAnalyzer(empty_rtt_data)

        self.assertEqual(analyzer.get_min_rtt(), 0.0)
        self.assertEqual(analyzer.get_max_rtt(), 0.0)
        self.assertEqual(len(analyzer.rtt_data), 0)

    def test_rtt_values_preservation(self):
        """Test that RTT values are correctly preserved."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import RTTAnalyzer

        analyzer = RTTAnalyzer(self.sample_data)

        # Check that all original RTT values are present
        expected_rtts = [10.5, 12.3, 8.9, 15.7, 11.2, 9.8, 13.4, 7.6, 14.1, 10.9]
        actual_rtts = analyzer.rtt_data.tolist()

        self.assertEqual(actual_rtts, expected_rtts)

    def test_rtt_analyzer_handles_none_values(self):
        """Test that analyzer handles None RTT values gracefully."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import RTTAnalyzer

        # Create data with None values mixed in
        data_with_nones = self.sample_data.copy()
        data_with_nones.loc[3, 'rtt'] = None

        analyzer = RTTAnalyzer(data_with_nones)

        # Should filter out None values
        self.assertNotIn(None, analyzer.rtt_data)


if __name__ == '__main__':
    unittest.main()
