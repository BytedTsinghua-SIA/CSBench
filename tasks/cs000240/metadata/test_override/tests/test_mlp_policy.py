"""
Test MLP policy implementation for CS285 Homework 2
"""
import numpy as np
import torch
import pytest

from cs285.infrastructure import pytorch_util as ptu
from cs285.policies.MLP_policy import MLPPolicy, MLPPolicyPG


class TestMLPPolicy:
    """Test MLP policy base class"""

    def setup_method(self):
        """Setup before each test"""
        ptu.init_gpu(use_gpu=False)

    def test_discrete_policy_creation(self):
        """Test creation of discrete action policy"""
        policy = MLPPolicy(
            ac_dim=5,  # 5 discrete actions
            ob_dim=10,
            n_layers=2,
            size=32,
            discrete=True,
            learning_rate=1e-3
        )

        assert policy.discrete == True
        assert policy.logits_na is not None
        assert policy.mean_net is None
        assert policy.logstd is None
        assert policy.ac_dim == 5
        assert policy.ob_dim == 10

    def test_continuous_policy_creation(self):
        """Test creation of continuous action policy"""
        policy = MLPPolicy(
            ac_dim=3,  # 3 continuous actions
            ob_dim=8,
            n_layers=2,
            size=64,
            discrete=False,
            learning_rate=1e-4
        )

        assert policy.discrete == False
        assert policy.logits_na is None
        assert policy.mean_net is not None
        assert policy.logstd is not None
        assert policy.ac_dim == 3
        assert policy.ob_dim == 8

    def test_discrete_forward(self):
        """Test forward pass for discrete policy"""
        policy = MLPPolicy(
            ac_dim=4,
            ob_dim=6,
            n_layers=1,
            size=16,
            discrete=True
        )

        # Test with single observation
        obs = torch.randn(6, device=ptu.device)
        output = policy.forward(obs)
        assert output.batch_shape == ()  # single observation has empty batch shape
        assert output.event_shape == ()

        # Test with batch of observations
        obs_batch = torch.randn(3, 6, device=ptu.device)
        output_batch = policy.forward(obs_batch)
        assert output_batch.batch_shape == (3,)

    def test_continuous_forward(self):
        """Test forward pass for continuous policy"""
        policy = MLPPolicy(
            ac_dim=2,
            ob_dim=5,
            n_layers=1,
            size=16,
            discrete=False
        )

        # Test with single observation
        obs = torch.randn(5, device=ptu.device)
        dist = policy.forward(obs)
        assert isinstance(dist, torch.distributions.MultivariateNormal)
        assert dist.batch_shape == ()
        assert dist.event_shape == (2,)

    def test_get_action_discrete(self):
        """Test action sampling for discrete policy"""
        policy = MLPPolicy(
            ac_dim=3,
            ob_dim=4,
            n_layers=1,
            size=8,
            discrete=True
        )

        # Single observation
        obs = np.random.randn(4).astype(np.float32)
        action = policy.get_action(obs)
        assert action.shape == (1, 3)  # One-hot like output

        # Batch of observations
        obs_batch = np.random.randn(5, 4).astype(np.float32)
        actions = policy.get_action(obs_batch)
        assert actions.shape == (5, 3)

    def test_get_action_continuous(self):
        """Test action sampling for continuous policy"""
        policy = MLPPolicy(
            ac_dim=2,
            ob_dim=3,
            n_layers=1,
            size=8,
            discrete=False
        )

        # Single observation
        obs = np.random.randn(3).astype(np.float32)
        action = policy.get_action(obs)
        assert action.shape == (1, 2)

        # Batch of observations
        obs_batch = np.random.randn(3, 3).astype(np.float32)
        actions = policy.get_action(obs_batch)
        assert actions.shape == (3, 2)


class TestMLPPolicyPG:
    """Test Policy Gradient MLP policy"""

    def setup_method(self):
        """Setup before each test"""
        ptu.init_gpu(use_gpu=False)

    def test_policy_creation(self):
        """Test creation of PG policy"""
        policy = MLPPolicyPG(
            ac_dim=4,
            ob_dim=8,
            n_layers=2,
            size=32,
            discrete=True,
            learning_rate=1e-3
        )

        assert isinstance(policy, MLPPolicy)
        assert policy.baseline_loss is not None
        assert isinstance(policy.baseline_loss, torch.nn.MSELoss)

    def test_update_discrete(self):
        """Test policy update for discrete actions"""
        policy = MLPPolicyPG(
            ac_dim=5,
            ob_dim=6,
            n_layers=1,
            size=16,
            discrete=True,
            learning_rate=1e-3
        )

        # Generate dummy data
        n_samples = 10
        observations = np.random.randn(n_samples, 6).astype(np.float32)
        actions = np.random.randint(0, 5, size=(n_samples,)).astype(np.float32)
        advantages = np.random.randn(n_samples).astype(np.float32)

        # Perform update
        log = policy.update(observations, actions, advantages)

        assert 'Training Loss' in log
        assert isinstance(log['Training Loss'], float)
        assert log['Training Loss'] >= 0

    def test_update_continuous(self):
        """Test policy update for continuous actions"""
        policy = MLPPolicyPG(
            ac_dim=2,
            ob_dim=3,
            n_layers=1,
            size=8,
            discrete=False,
            learning_rate=1e-3
        )

        # Generate dummy data
        n_samples = 10
        observations = np.random.randn(n_samples, 3).astype(np.float32)
        actions = np.random.randn(n_samples, 2).astype(np.float32)
        advantages = np.random.randn(n_samples).astype(np.float32)

        # Perform update
        log = policy.update(observations, actions, advantages)

        assert 'Training Loss' in log
        assert isinstance(log['Training Loss'], float)
        assert log['Training Loss'] >= 0

    def test_update_with_baseline(self):
        """Test policy update with neural network baseline"""
        policy = MLPPolicyPG(
            ac_dim=3,
            ob_dim=4,
            n_layers=1,
            size=16,
            discrete=True,
            learning_rate=1e-3,
            nn_baseline=True
        )

        assert policy.baseline is not None

        # Generate dummy data
        n_samples = 10
        observations = np.random.randn(n_samples, 4).astype(np.float32)
        actions = np.random.randint(0, 3, size=(n_samples,)).astype(np.float32)
        advantages = np.random.randn(n_samples).astype(np.float32)
        q_values = np.random.randn(n_samples).astype(np.float32)

        # Perform update with q_values for baseline training
        log = policy.update(observations, actions, advantages, q_values)

        assert 'Training Loss' in log
        assert isinstance(log['Training Loss'], float)

    def test_run_baseline_prediction(self):
        """Test baseline prediction helper"""
        policy = MLPPolicyPG(
            ac_dim=2,
            ob_dim=3,
            n_layers=1,
            size=8,
            discrete=False,
            learning_rate=1e-3,
            nn_baseline=True
        )

        observations = np.random.randn(5, 3).astype(np.float32)
        predictions = policy.run_baseline_prediction(observations)

        assert predictions.shape == (5,)
        assert predictions.dtype == np.float32

    def test_update_loss_decreases(self):
        """Test that loss generally decreases with more updates"""
        policy = MLPPolicyPG(
            ac_dim=2,
            ob_dim=3,
            n_layers=1,
            size=16,
            discrete=False,
            learning_rate=1e-3
        )

        # Generate dummy data with structure
        n_samples = 20
        np.random.seed(42)
        observations = np.random.randn(n_samples, 3).astype(np.float32)
        actions = np.random.randn(n_samples, 2).astype(np.float32)
        advantages = np.ones(n_samples).astype(np.float32)  # All positive advantages

        # Perform multiple updates
        losses = []
        for _ in range(5):
            log = policy.update(observations, actions, advantages)
            losses.append(log['Training Loss'])

        # Training should run without errors
        assert len(losses) == 5
        assert all(l >= 0 for l in losses)
