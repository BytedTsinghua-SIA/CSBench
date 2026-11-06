import unittest

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class TestLossCorrelationAnalyzer(unittest.TestCase):
    """Unit tests for LossCorrelationAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample data with alternating received/lost pattern
        timestamps = pd.date_range('2023-01-01', periods=20, freq='200ms')
        received_pattern = [True, False, True, False, True, True, False, True,
                          False, True, True, False, False, True, True, True,
                          False, True, False, True]

        self.sample_data = pd.DataFrame({
            'timestamp': timestamps,
            'sequence': list(range(1, 21)),
            'rtt': [10.0] * 20,
            'received': received_pattern
        })

    def test_calculate_autocorrelation_returns_dict(self):
        """Test that autocorrelation calculation returns a dictionary."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import LossCorrelationAnalyzer

        analyzer = LossCorrelationAnalyzer(self.sample_data)
        result = analyzer.calculate_autocorrelation(max_lag=5)

        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

        # Should have keys for lags from -5 to 5 (excluding 0)
        expected_keys = list(range(-5, 0)) + list(range(1, 6))
        for key in expected_keys:
            self.assertIn(key, result)

    def test_autocorrelation_result_structure(self):
        """Test that each autocorrelation result has the correct structure."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import LossCorrelationAnalyzer

        analyzer = LossCorrelationAnalyzer(self.sample_data)
        result = analyzer.calculate_autocorrelation(max_lag=3)

        # Check structure of one result
        lag_result = result[1]  # lag = 1
        expected_keys = [
            'prob_success_given_success',
            'prob_success_given_loss',
            'count_success',
            'count_loss'
        ]

        for key in expected_keys:
            self.assertIn(key, lag_result)
            self.assertIsInstance(lag_result[key], (int, float))

    def test_get_overall_delivery_rate(self):
        """Test calculation of overall delivery rate."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import LossCorrelationAnalyzer

        analyzer = LossCorrelationAnalyzer(self.sample_data)
        rate = analyzer.get_overall_delivery_rate()

        # In our sample data, 12 out of 20 packets were received
        expected_rate = 12 / 20
        self.assertAlmostEqual(rate, expected_rate, places=5)

    def test_autocorrelation_with_small_max_lag(self):
        """Test autocorrelation with small max_lag value."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import LossCorrelationAnalyzer

        analyzer = LossCorrelationAnalyzer(self.sample_data)
        result = analyzer.calculate_autocorrelation(max_lag=1)

        # Should only have lag = -1 and lag = 1
        self.assertIn(-1, result)
        self.assertIn(1, result)
        self.assertNotIn(0, result)
        self.assertNotIn(2, result)

    def test_autocorrelation_probabilities_in_range(self):
        """Test that calculated probabilities are in valid range [0, 1]."""
        if not HAS_PANDAS:
            self.skipTest("pandas not available")

        from network_path_analyzer import LossCorrelationAnalyzer

        analyzer = LossCorrelationAnalyzer(self.sample_data)
        result = analyzer.calculate_autocorrelation(max_lag=3)

        for lag, lag_result in result.items():
            prob_success_given_success = lag_result['prob_success_given_success']
            prob_success_given_loss = lag_result['prob_success_given_loss']

            self.assertGreaterEqual(prob_success_given_success, 0.0)
            self.assertLessEqual(prob_success_given_success, 1.0)
            self.assertGreaterEqual(prob_success_given_loss, 0.0)
            self.assertLessEqual(prob_success_given_loss, 1.0)


if __name__ == '__main__':
    unittest.main()
