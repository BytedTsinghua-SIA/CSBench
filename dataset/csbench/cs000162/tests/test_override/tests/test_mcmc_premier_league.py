"""
Unit tests for MCMC Premier League Model

Tests core functionality:
- Parameter packing/unpacking
- Log likelihood computation
- Metropolis-Hastings algorithm
- Posterior statistics computation
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcmc_premier_league import PremierLeagueMCMC


class TestPremierLeagueMCMC(unittest.TestCase):
    """Test cases for Premier League MCMC"""

    def setUp(self):
        """Set up test fixtures"""
        # Create mock data: 10 games, 4 columns [y_g0, y_g1, h(g), a(g)]
        self.sample_data = np.array([
            [2, 1, 0, 1],
            [1, 0, 1, 2],
            [3, 2, 2, 3],
            [0, 1, 3, 4],
            [2, 2, 4, 5],
            [1, 1, 5, 6],
            [2, 0, 6, 7],
            [1, 3, 7, 8],
            [0, 2, 8, 9],
            [3, 1, 9, 0],
        ])
        self.mcmc = PremierLeagueMCMC(self.sample_data)

    def test_initialization(self):
        """Test MCMC model initialization"""
        self.assertEqual(self.mcmc.num_games, 10)
        self.assertEqual(self.mcmc.num_teams, 20)
        self.assertEqual(self.mcmc.tau0, 0.0001)
        self.assertEqual(self.mcmc.alpha, 0.1)

    def test_param_dimension(self):
        """Test parameter dimension is correct"""
        # 1 (home) + 19 (att) + 19 (def) + 2 (mu) + 2 (tau) = 43
        expected_dim = 1 + 19 + 19 + 2 + 2
        self.assertEqual(self.mcmc.param_dim, expected_dim)

    def test_unpack_params_format(self):
        """Test parameter unpacking returns correct format"""
        params = np.random.randn(self.mcmc.param_dim)
        # Ensure tau parameters are positive
        params[-2] = abs(params[-2])
        params[-1] = abs(params[-1])
        
        param_dict = self.mcmc._unpack_params(params)
        
        self.assertIn('home', param_dict)
        self.assertIn('att', param_dict)
        self.assertIn('def', param_dict)
        self.assertIn('mu_att', param_dict)
        self.assertIn('mu_def', param_dict)
        self.assertIn('tau_att', param_dict)
        self.assertIn('tau_def', param_dict)

    def test_unpack_params_dimensions(self):
        """Test unpacked parameters have correct dimensions"""
        params = np.random.randn(self.mcmc.param_dim)
        params[-2] = abs(params[-2])
        params[-1] = abs(params[-1])
        
        param_dict = self.mcmc._unpack_params(params)
        
        self.assertIsInstance(param_dict['home'], (float, np.floating))
        self.assertEqual(len(param_dict['att']), self.mcmc.num_teams)
        self.assertEqual(len(param_dict['def']), self.mcmc.num_teams)
        self.assertIsInstance(param_dict['mu_att'], (float, np.floating))
        self.assertIsInstance(param_dict['tau_att'], (float, np.floating))

    def test_unpack_params_constraints(self):
        """Test unpacked parameters satisfy constraints"""
        params = np.random.randn(self.mcmc.param_dim)
        params[-2] = abs(params[-2])
        params[-1] = abs(params[-1])
        
        param_dict = self.mcmc._unpack_params(params)
        
        # Team 0 should have att=0, def=0 (identifiability constraint)
        self.assertEqual(param_dict['att'][0], 0.0)
        self.assertEqual(param_dict['def'][0], 0.0)

    def test_pack_params_roundtrip(self):
        """Test pack/unpack roundtrip"""
        params = np.random.randn(self.mcmc.param_dim)
        params[-2] = abs(params[-2])
        params[-1] = abs(params[-1])
        
        param_dict = self.mcmc._unpack_params(params)
        repacked = self.mcmc._pack_params(param_dict)
        
        np.testing.assert_allclose(params, repacked, rtol=1e-10)

    def test_compute_log_likelihood_format(self):
        """Test log likelihood computation returns valid format"""
        params = np.random.randn(self.mcmc.param_dim) * 0.1
        params[-2] = abs(params[-2]) + 0.1  # Ensure positive tau
        params[-1] = abs(params[-1]) + 0.1
        
        log_likelihood = self.mcmc._compute_log_likelihood(params)
        
        self.assertIsInstance(log_likelihood, float)
        self.assertTrue(np.isfinite(log_likelihood))

    def test_compute_log_likelihood_consistency(self):
        """Test log likelihood is consistent"""
        params = np.random.randn(self.mcmc.param_dim) * 0.1
        params[-2] = abs(params[-2]) + 0.1
        params[-1] = abs(params[-1]) + 0.1
        
        ll1 = self.mcmc._compute_log_likelihood(params)
        ll2 = self.mcmc._compute_log_likelihood(params)
        
        self.assertAlmostEqual(ll1, ll2, places=5)

    def test_metropolis_hastings_output_format(self):
        """Test Metropolis-Hastings output format"""
        np.random.seed(42)
        samples, acceptance_flags = self.mcmc.metropolis_hastings(
            sigma=0.05,
            num_burnin=10,
            num_samples=5,
            thinning=1,
            start_point=0.1
        )
        
        self.assertIsInstance(samples, np.ndarray)
        self.assertEqual(samples.shape[1], self.mcmc.param_dim)
        self.assertIsInstance(acceptance_flags, list)

    def test_metropolis_hastings_sample_count(self):
        """Test Metropolis-Hastings collects correct number of samples"""
        np.random.seed(42)
        num_samples = 5
        samples, _ = self.mcmc.metropolis_hastings(
            sigma=0.05,
            num_burnin=10,
            num_samples=num_samples,
            thinning=1,
            start_point=0.1
        )
        
        self.assertEqual(len(samples), num_samples)

    def test_metropolis_hastings_thinning(self):
        """Test Metropolis-Hastings thinning"""
        np.random.seed(42)
        num_samples = 3
        thinning = 2
        samples, _ = self.mcmc.metropolis_hastings(
            sigma=0.05,
            num_burnin=5,
            num_samples=num_samples,
            thinning=thinning,
            start_point=0.1
        )
        
        # Should collect num_samples samples
        self.assertEqual(len(samples), num_samples)

    def test_acceptance_flags_format(self):
        """Test acceptance flags format"""
        np.random.seed(42)
        num_burnin = 5
        num_samples = 3
        thinning = 1
        total_steps = num_burnin + num_samples * thinning
        
        _, acceptance_flags = self.mcmc.metropolis_hastings(
            sigma=0.05,
            num_burnin=num_burnin,
            num_samples=num_samples,
            thinning=thinning,
            start_point=0.1
        )
        
        self.assertIsInstance(acceptance_flags, list)
        # Flags should be boolean-like
        for flag in acceptance_flags:
            self.assertIsInstance(flag, (bool, np.bool_))

    def test_compute_posterior_means_format(self):
        """Test posterior means computation format"""
        # Create mock samples
        num_samples = 10
        samples = np.random.randn(num_samples, self.mcmc.param_dim) * 0.1
        samples[:, -2] = abs(samples[:, -2]) + 0.1
        samples[:, -1] = abs(samples[:, -1]) + 0.1
        
        posterior_means = self.mcmc.compute_posterior_means(samples)
        
        self.assertIn('home', posterior_means)
        self.assertIn('att', posterior_means)
        self.assertIn('def', posterior_means)
        self.assertIn('mu_att', posterior_means)
        self.assertIn('tau_att', posterior_means)

    def test_posterior_means_dimensions(self):
        """Test posterior means have correct dimensions"""
        num_samples = 10
        samples = np.random.randn(num_samples, self.mcmc.param_dim) * 0.1
        samples[:, -2] = abs(samples[:, -2]) + 0.1
        samples[:, -1] = abs(samples[:, -1]) + 0.1
        
        posterior_means = self.mcmc.compute_posterior_means(samples)
        
        self.assertEqual(len(posterior_means['att']), self.mcmc.num_teams)
        self.assertEqual(len(posterior_means['def']), self.mcmc.num_teams)
        self.assertIsInstance(posterior_means['home'], (float, np.floating))

    def test_posterior_means_constraints(self):
        """Test posterior means satisfy constraints"""
        num_samples = 10
        samples = np.random.randn(num_samples, self.mcmc.param_dim) * 0.1
        samples[:, -2] = abs(samples[:, -2]) + 0.1
        samples[:, -1] = abs(samples[:, -1]) + 0.1
        
        posterior_means = self.mcmc.compute_posterior_means(samples)
        
        # Team 0 should have att=0, def=0
        self.assertAlmostEqual(posterior_means['att'][0], 0.0, places=5)
        self.assertAlmostEqual(posterior_means['def'][0], 0.0, places=5)


    def test_team_names_length(self):
        """Test team names list has correct length"""
        self.assertEqual(len(self.mcmc.team_names), self.mcmc.num_teams)


if __name__ == "__main__":
    unittest.main()

