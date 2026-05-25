"""
Test MLP policy implementation for CS285 Homework 1
"""
import numpy as np
import torch
import pytest

from cs285.infrastructure import pytorch_util as ptu
from cs285.policies.MLP_policy import MLPPolicy, MLPPolicySL


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
        assert output.shape == (4,)  # logits for 4 actions
        
        # Test with batch of observations
        obs_batch = torch.randn(3, 6, device=ptu.device)
        output_batch = policy.forward(obs_batch)
        assert output_batch.shape == (3, 4)
        
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
        assert isinstance(dist, torch.distributions.Normal)
        assert dist.mean.shape == (2,)
        assert dist.stddev.shape == (2,)
        
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


class TestMLPPolicySL:
    """Test supervised learning policy for behavioral cloning"""
    
    def setup_method(self):
        """Setup before each test"""
        ptu.init_gpu(use_gpu=False)
        
    def test_policy_creation(self):
        """Test creation of SL policy"""
        policy = MLPPolicySL(
            ac_dim=2,
            ob_dim=4,
            n_layers=2,
            size=32,
            discrete=False
        )
        
        assert isinstance(policy, MLPPolicy)
        assert policy.loss is not None
        assert isinstance(policy.loss, torch.nn.MSELoss)
        
    def test_continuous_forward_sl(self):
        """Test forward pass for continuous SL policy (should return means)"""
        policy = MLPPolicySL(
            ac_dim=3,
            ob_dim=5,
            n_layers=1,
            size=16,
            discrete=False
        )
        
        obs = torch.randn(2, 5, device=ptu.device)
        output = policy.forward(obs)
        # Should return raw means, not distribution
        assert output.shape == (2, 3)
        assert not isinstance(output, torch.distributions.Distribution)
        
    def test_discrete_forward_sl(self):
        """Test forward pass for discrete SL policy"""
        policy = MLPPolicySL(
            ac_dim=4,
            ob_dim=6,
            n_layers=1,
            size=16,
            discrete=True
        )
        
        obs = torch.randn(3, 6, device=ptu.device)
        output = policy.forward(obs)
        # Should return logits
        assert output.shape == (3, 4)
        
    def test_update_continuous(self):
        """Test policy update for continuous actions"""
        policy = MLPPolicySL(
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
        
        # Perform update
        log = policy.update(observations, actions)
        
        assert 'Training Loss' in log
        assert isinstance(log['Training Loss'], float)
        assert log['Training Loss'] >= 0
        
    def test_update_discrete(self):
        """Test policy update for discrete actions"""
        policy = MLPPolicySL(
            ac_dim=5,
            ob_dim=4,
            n_layers=1,
            size=8,
            discrete=True,
            learning_rate=1e-3
        )
        
        # Generate dummy data
        n_samples = 10
        observations = np.random.randn(n_samples, 4).astype(np.float32)
        actions = np.random.randn(n_samples, 5).astype(np.float32)  # Logits
        
        # Perform update
        log = policy.update(observations, actions)
        
        assert 'Training Loss' in log
        assert isinstance(log['Training Loss'], float)
        assert log['Training Loss'] >= 0
        
    def test_save_load(self, tmp_path):
        """Test policy saving and loading"""
        policy = MLPPolicySL(
            ac_dim=2,
            ob_dim=3,
            n_layers=1,
            size=8,
            discrete=False
        )
        
        # Save policy
        save_path = tmp_path / "test_policy.pt"
        policy.save(save_path)
        assert save_path.exists()
        
        # Note: Loading would require a separate load method
        # For now, just verify save works