"""
Integration tests for CS285 Homework 1
"""
import numpy as np
import pytest
import pickle
import tempfile
import os

from cs285.infrastructure.utils import (
    sample_trajectory, 
    sample_trajectories,
    sample_n_trajectories,
    Path,
    convert_listofrollouts,
    get_pathlength
)
from cs285.infrastructure.replay_buffer import ReplayBuffer
from cs285.policies.MLP_policy import MLPPolicySL
from cs285.infrastructure import pytorch_util as ptu


class MockPolicy:
    """Mock policy for testing trajectory sampling"""
    def __init__(self, action_dim, discrete=False):
        self.action_dim = action_dim
        self.discrete = discrete
        
    def get_action(self, obs):
        if len(obs.shape) == 1:
            batch_size = 1
        else:
            batch_size = obs.shape[0]
            
        if self.discrete:
            # Return one-hot like output
            actions = np.zeros((batch_size, self.action_dim))
            actions[:, 0] = 1.0  # Always choose action 0
        else:
            actions = np.random.randn(batch_size, self.action_dim)
            
        return actions


class MockEnv:
    """Mock environment for testing"""
    def __init__(self, obs_dim=4, action_dim=2, discrete=False, max_steps=100):
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.discrete = discrete
        self.max_steps = max_steps
        self.step_count = 0
        
    def reset(self):
        self.step_count = 0
        obs = np.random.randn(self.obs_dim).astype(np.float32)
        return obs, {}  # New gym API returns (obs, info)
        
    def step(self, action):
        self.step_count += 1
        obs = np.random.randn(self.obs_dim).astype(np.float32)
        reward = 1.0
        done = self.step_count >= self.max_steps
        truncated = False
        info = {}
        
        return obs, reward, done, truncated, info
        
    def render(self):
        return np.zeros((64, 64, 3), dtype=np.uint8)


class TestIntegration:
    """Integration tests for CS285 HW1 components"""
    
    def setup_method(self):
        """Setup before each test"""
        ptu.init_gpu(use_gpu=False)
        
    def test_path_creation(self):
        """Test Path data structure"""
        obs = np.random.randn(5, 3).astype(np.float32)
        image_obs = [np.zeros((64, 64, 3), dtype=np.uint8) for _ in range(5)]
        acs = np.random.randn(5, 2).astype(np.float32)
        rewards = np.random.randn(5).astype(np.float32)
        next_obs = np.random.randn(5, 3).astype(np.float32)
        terminals = np.array([0, 0, 0, 1, 0], dtype=np.float32)
        
        path = Path(obs, image_obs, acs, rewards, next_obs, terminals)
        
        assert 'observation' in path
        assert 'image_obs' in path
        assert 'action' in path
        assert 'reward' in path
        assert 'next_observation' in path
        assert 'terminal' in path
        
        assert path['observation'].shape == (5, 3)
        assert path['action'].shape == (5, 2)
        assert path['reward'].shape == (5,)
        assert path['next_observation'].shape == (5, 3)
        assert path['terminal'].shape == (5,)
        
        if len(image_obs) > 0:
            assert path['image_obs'].shape == (5, 64, 64, 3)
            
    def test_convert_listofrollouts(self):
        """Test conversion of rollouts to arrays"""
        # Create multiple paths
        paths = []
        for _ in range(3):
            path = Path(
                obs=np.random.randn(2, 4).astype(np.float32),
                image_obs=[],
                acs=np.random.randn(2, 2).astype(np.float32),
                rewards=np.random.randn(2).astype(np.float32),
                next_obs=np.random.randn(2, 4).astype(np.float32),
                terminals=np.array([0, 1], dtype=np.float32)
            )
            paths.append(path)
            
        # Convert to arrays
        obs, acs, rewards, next_obs, terminals = convert_listofrollouts(paths)
        
        # Check shapes
        assert obs.shape == (6, 4)  # 3 paths * 2 steps each
        assert acs.shape == (6, 2)
        assert rewards.shape == (6,)
        assert next_obs.shape == (6, 4)
        assert terminals.shape == (6,)
        
    def test_get_pathlength(self):
        """Test path length calculation"""
        path = Path(
            obs=np.random.randn(7, 3).astype(np.float32),
            image_obs=[],
            acs=np.random.randn(7, 2).astype(np.float32),
            rewards=np.random.randn(7).astype(np.float32),
            next_obs=np.random.randn(7, 3).astype(np.float32),
            terminals=np.zeros(7).astype(np.float32)
        )
        
        length = get_pathlength(path)
        assert length == 7
        
    def test_sample_trajectory_mock(self):
        """Test single trajectory sampling with mock env"""
        env = MockEnv(obs_dim=5, action_dim=2, max_steps=10)
        policy = MockPolicy(action_dim=2)
        
        path = sample_trajectory(env, policy, max_path_length=20, render=False)
        
        assert 'observation' in path
        assert 'action' in path
        assert 'reward' in path
        assert 'next_observation' in path
        assert 'terminal' in path
        
        # Path should have at most max_steps (10) but could terminate earlier
        path_length = get_pathlength(path)
        assert path_length <= 10
        assert path_length > 0
        
    def test_sample_trajectories_mock(self):
        """Test batch trajectory sampling with mock env"""
        env = MockEnv(obs_dim=4, action_dim=2, max_steps=5)
        policy = MockPolicy(action_dim=2)
        
        min_timesteps = 15
        max_path_length = 10
        
        paths, timesteps = sample_trajectories(
            env, policy, min_timesteps, max_path_length, render=False
        )
        
        assert timesteps >= min_timesteps
        assert len(paths) > 0
        
        # Verify total timesteps
        total_timesteps = sum(get_pathlength(p) for p in paths)
        assert total_timesteps == timesteps
        
    def test_sample_n_trajectories_mock(self):
        """Test sampling exactly n trajectories"""
        env = MockEnv(obs_dim=3, action_dim=1, max_steps=3)
        policy = MockPolicy(action_dim=1)
        
        ntraj = 4
        max_path_length = 5
        
        paths = sample_n_trajectories(
            env, policy, ntraj, max_path_length, render=False
        )
        
        assert len(paths) == ntraj
        
        # Each path should have at most max_steps (3)
        for path in paths:
            path_length = get_pathlength(path)
            assert path_length <= 3
            assert path_length > 0
            
    def test_replay_buffer_integration(self):
        """Test replay buffer with sampled trajectories"""
        # Create sample data
        paths = []
        for _ in range(2):
            path = Path(
                obs=np.random.randn(3, 4).astype(np.float32),
                image_obs=[],
                acs=np.random.randn(3, 2).astype(np.float32),
                rewards=np.random.randn(3).astype(np.float32),
                next_obs=np.random.randn(3, 4).astype(np.float32),
                terminals=np.array([0, 0, 1], dtype=np.float32)
            )
            paths.append(path)
            
        # Add to buffer
        buffer = ReplayBuffer(max_size=1000)
        buffer.add_rollouts(paths)
        
        # Sample from buffer
        batch_size = 4
        obs, acs, rews, next_obs, terminals = buffer.sample_random_data(batch_size)
        
        # Verify shapes
        assert obs.shape == (batch_size, 4)
        assert acs.shape == (batch_size, 2)
        assert rews.shape == (batch_size,)
        assert next_obs.shape == (batch_size, 4)
        assert terminals.shape == (batch_size,)
        
    def test_policy_training_integration(self):
        """Test policy training with replay buffer data"""
        # Create policy
        policy = MLPPolicySL(
            ac_dim=2,
            ob_dim=4,
            n_layers=1,
            size=16,
            discrete=False,
            learning_rate=1e-3
        )
        
        # Create training data
        n_samples = 20
        observations = np.random.randn(n_samples, 4).astype(np.float32)
        actions = np.random.randn(n_samples, 2).astype(np.float32)
        
        # Train policy
        log = policy.update(observations, actions)
        
        assert 'Training Loss' in log
        loss = log['Training Loss']
        assert isinstance(loss, float)
        assert loss >= 0
        
        # Test action prediction
        test_obs = np.random.randn(3, 4).astype(np.float32)
        actions = policy.get_action(test_obs)
        
        assert actions.shape == (3, 2)
        
    def test_expert_data_pickle(self):
        """Test expert data pickle format (simulated)"""
        # Create dummy expert data
        expert_data = [
            {
                'observation': np.random.randn(100, 8).astype(np.float32),
                'action': np.random.randn(100, 2).astype(np.float32),
                'reward': np.random.randn(100).astype(np.float32),
                'next_observation': np.random.randn(100, 8).astype(np.float32),
                'terminal': np.zeros(100).astype(np.float32)
            }
        ]
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            pickle.dump(expert_data, f)
            temp_path = f.name
            
        try:
            # Load back
            with open(temp_path, 'rb') as f:
                loaded_data = pickle.load(f)
                
            # Verify
            assert len(loaded_data) == 1
            assert 'observation' in loaded_data[0]
            assert 'action' in loaded_data[0]
            assert loaded_data[0]['observation'].shape == (100, 8)
            
        finally:
            # Clean up
            os.unlink(temp_path)
            
    def test_full_training_cycle(self):
        """Simulate a full training cycle"""
        # 1. Create policy
        policy = MLPPolicySL(
            ac_dim=2,
            ob_dim=4,
            n_layers=2,
            size=32,
            discrete=False,
            learning_rate=1e-3
        )
        
        # 2. Create replay buffer
        buffer = ReplayBuffer(max_size=10000)
        
        # 3. Generate expert-like data
        expert_paths = []
        for _ in range(3):
            path = Path(
                obs=np.random.randn(5, 4).astype(np.float32),
                image_obs=[],
                acs=np.random.randn(5, 2).astype(np.float32),
                rewards=np.ones(5).astype(np.float32) * 10.0,  # Expert gets high rewards
                next_obs=np.random.randn(5, 4).astype(np.float32),
                terminals=np.array([0, 0, 0, 0, 1], dtype=np.float32)
            )
            expert_paths.append(path)
            
        # 4. Add to buffer
        buffer.add_rollouts(expert_paths)
        
        # 5. Train for several iterations
        losses = []
        for _ in range(10):
            # Sample batch
            obs, acs, _, _, _ = buffer.sample_random_data(batch_size=8)
            
            # Update policy
            log = policy.update(obs, acs)
            losses.append(log['Training Loss'])
            
        # Loss should generally decrease (not strictly guaranteed)
        # but we can check that training runs without errors
        assert len(losses) == 10
        assert all(l >= 0 for l in losses)
        
        # 6. Test trained policy
        test_obs = np.random.randn(2, 4).astype(np.float32)
        actions = policy.get_action(test_obs)
        assert actions.shape == (2, 2)
        
    def test_different_batch_sizes(self):
        """Test training with different batch sizes"""
        policy = MLPPolicySL(
            ac_dim=3,
            ob_dim=5,
            n_layers=1,
            size=16,
            discrete=False,
            learning_rate=1e-3
        )
        
        # Test various batch sizes
        for batch_size in [1, 4, 16, 32]:
            # Generate data
            obs = np.random.randn(batch_size, 5).astype(np.float32)
            acs = np.random.randn(batch_size, 3).astype(np.float32)
            
            # Train
            log = policy.update(obs, acs)
            
            assert 'Training Loss' in log
            assert isinstance(log['Training Loss'], float)
            
    def test_policy_with_discrete_actions(self):
        """Test policy with discrete action space"""
        policy = MLPPolicySL(
            ac_dim=5,  # 5 discrete actions
            ob_dim=4,
            n_layers=1,
            size=16,
            discrete=True,
            learning_rate=1e-3
        )
        
        # Generate data (one-hot encoded actions for discrete)
        n_samples = 10
        observations = np.random.randn(n_samples, 4).astype(np.float32)
        actions = np.zeros((n_samples, 5)).astype(np.float32)
        actions[:, 0] = 1.0  # All choose action 0
        
        # Train
        log = policy.update(observations, actions)
        
        assert 'Training Loss' in log
        assert log['Training Loss'] >= 0
        
        # Test inference
        test_obs = np.random.randn(3, 4).astype(np.float32)
        action_logits = policy.get_action(test_obs)
        
        assert action_logits.shape == (3, 5)