import unittest

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class TestDeliveryStatistics(unittest.TestCase):
    """Unit tests for DeliveryStatistics class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample data for testing
        timestamps = pd.date_range('2023-01-01', periods=10, freq='200ms')
        self.sample_data_all_received = pd.DataFrame({
            'timestamp': timestamps,
            'sequence': list(range(1, 11)),
            'rtt': [10.0] * 10,
            'received': [True] * 10
        })

        self.sample_data_mixed = pd.DataFrame({
            'timestamp': timestamps,
            'sequence': list(range(1, 11)),
            'rtt': [10.0] * 10,
            'received': [True, False, True, True, False, True, False, False, True, True]
        })

    def test_calculate_overall_delivery_rate_perfect(self):
        """Test delivery rate calculation for perfect delivery."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import DeliveryStatistics

        stats = DeliveryStatistics(self.sample_data_all_received)
        rate = stats.calculate_overall_delivery_rate()

        self.assertEqual(rate, 1.0)

    def test_calculate_overall_delivery_rate_mixed(self):
        """Test delivery rate calculation for mixed delivery."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import DeliveryStatistics

        stats = DeliveryStatistics(self.sample_data_mixed)
        rate = stats.calculate_overall_delivery_rate()

        self.assertEqual(rate, 0.6)  # 6 out of 10 received

    def test_find_longest_consecutive_successes_all_true(self):
        """Test finding longest consecutive successes when all are successful."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import DeliveryStatistics

        stats = DeliveryStatistics(self.sample_data_all_received)
        longest = stats.find_longest_consecutive_successes()

        self.assertEqual(longest, 10)

    def test_find_longest_consecutive_successes_mixed(self):
        """Test finding longest consecutive successes in mixed data."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import DeliveryStatistics

        stats = DeliveryStatistics(self.sample_data_mixed)
        longest = stats.find_longest_consecutive_successes()

        self.assertEqual(longest, 2)  # Positions 3-4 are consecutive successes

    def test_find_longest_consecutive_losses_no_losses(self):
        """Test finding longest consecutive losses when there are no losses."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import DeliveryStatistics

        stats = DeliveryStatistics(self.sample_data_all_received)
        longest = stats.find_longest_consecutive_losses()

        self.assertEqual(longest, 0)

    def test_find_longest_consecutive_losses_mixed(self):
        """Test finding longest consecutive losses in mixed data."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import DeliveryStatistics

        stats = DeliveryStatistics(self.sample_data_mixed)
        longest = stats.find_longest_consecutive_losses()

        self.assertEqual(longest, 2)  # Positions 7-8 are consecutive losses

    def test_empty_dataframe_handling(self):
        """Test behavior with empty dataframe."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import DeliveryStatistics

        empty_data = pd.DataFrame(columns=['timestamp', 'sequence', 'rtt', 'received'])
        stats = DeliveryStatistics(empty_data)

        self.assertEqual(stats.calculate_overall_delivery_rate(), 0.0)
        self.assertEqual(stats.find_longest_consecutive_successes(), 0)
        self.assertEqual(stats.find_longest_consecutive_losses(), 0)


if __name__ == '__main__':
    unittest.main()
