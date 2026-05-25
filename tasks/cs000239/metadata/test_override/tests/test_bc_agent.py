"""
Test BC agent implementation for CS285 Homework 1
"""
import numpy as np
import pytest
import gym
from unittest.mock import Mock, MagicMock

from cs285.agents.bc_agent import BCAgent
from cs285.infrastructure import pytorch_util as ptu


class TestBCAgent:
    """Test behavioral cloning agent"""
    
    def setup_method(self):
        """Setup before each test"""
        ptu.init_gpu(use_gpu=False)
        
    def create_mock_env(self, discrete=False):
        """Create a mock environment for testing"""
        env = Mock(spec=gym.Env)
        
        if discrete:
            action_space = Mock(spec=gym.spaces.Discrete)
            action_space.n = 5
        else:
            action_space = Mock(spec=gym.spaces.Box)
            action_space.shape = (3,)
            
        observation_space = Mock(spec=gym.spaces.Box)
        observation_space.shape = (8,)
        
        env.action_space = action_space
        env.observation_space = observation_space
        
        return env
    
    def test_agent_creation_continuous(self):
        """Test creation of BC agent for continuous actions"""
        env = self.create_mock_env(discrete=False)
        
        agent_params = {
            'ac_dim': 3,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': False,
            'learning_rate': 1e-3,
            'max_replay_buffer_size': 10000
        }
        
        agent = BCAgent(env, agent_params)
        
        assert agent.env == env
        assert agent.agent_params == agent_params
        assert agent.replay_buffer is not None
        assert agent.actor is not None
        
        # Check actor properties
        assert agent.actor.ac_dim == 3
        assert agent.actor.ob_dim == 8
        assert agent.actor.discrete == False
        
    def test_agent_creation_discrete(self):
        """Test creation of BC agent for discrete actions"""
        env = self.create_mock_env(discrete=True)
        
        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 1,
            'size': 16,
            'discrete': True,
            'learning_rate': 1e-4,
            'max_replay_buffer_size': 5000
        }
        
        agent = BCAgent(env, agent_params)
        
        assert agent.actor.discrete == True
        assert agent.actor.ac_dim == 5
        
    def test_add_to_replay_buffer(self):
        """Test adding paths to replay buffer"""
        env = self.create_mock_env(discrete=False)
        
        agent_params = {
            'ac_dim': 2,
            'ob_dim': 4,
            'n_layers': 1,
            'size': 8,
            'discrete': False,
            'learning_rate': 1e-3,
            'max_replay_buffer_size': 1000
        }
        
        agent = BCAgent(env, agent_params)
        
        # Create dummy paths
        paths = [
            {
                'observation': np.random.randn(3, 4).astype(np.float32),
                'action': np.random.randn(3, 2).astype(np.float32),
                'reward': np.random.randn(3).astype(np.float32),
                'next_observation': np.random.randn(3, 4).astype(np.float32),
                'terminal': np.zeros(3).astype(np.float32)
            },
            {
                'observation': np.random.randn(2, 4).astype(np.float32),
                'action': np.random.randn(2, 2).astype(np.float32),
                'reward': np.random.randn(2).astype(np.float32),
                'next_observation': np.random.randn(2, 4).astype(np.float32),
                'terminal': np.ones(2).astype(np.float32)
            }
        ]
        
        # Add to buffer
        initial_buffer_size = len(agent.replay_buffer)
        agent.add_to_replay_buffer(paths)
        
        # Buffer should now have data
        assert len(agent.replay_buffer) > initial_buffer_size
        assert len(agent.replay_buffer) == 5  # 3 + 2 transitions
        
    def test_train_method(self):
        """Test agent training method"""
        env = self.create_mock_env(discrete=False)
        
        agent_params = {
            'ac_dim': 2,
            'ob_dim': 3,
            'n_layers': 1,
            'size': 8,
            'discrete': False,
            'learning_rate': 1e-3,
            'max_replay_buffer_size': 1000
        }
        
        agent = BCAgent(env, agent_params)
        
        # Create dummy batch data
        batch_size = 4
        ob_no = np.random.randn(batch_size, 3).astype(np.float32)
        ac_na = np.random.randn(batch_size, 2).astype(np.float32)
        re_n = np.random.randn(batch_size).astype(np.float32)
        next_ob_no = np.random.randn(batch_size, 3).astype(np.float32)
        terminal_n = np.zeros(batch_size).astype(np.float32)
        
        # Train agent
        log = agent.train(ob_no, ac_na, re_n, next_ob_no, terminal_n)
        
        # Check training log
        assert 'Training Loss' in log
        assert isinstance(log['Training Loss'], float)
        assert log['Training Loss'] >= 0
        
        # Note: re_n, next_ob_no, terminal_n are not used in BC training
        # but are included for interface compatibility
        
    def test_sample_method(self):
        """Test sampling from replay buffer"""
        env = self.create_mock_env(discrete=False)
        
        agent_params = {
            'ac_dim': 2,
            'ob_dim': 3,
            'n_layers': 1,
            'size': 8,
            'discrete': False,
            'learning_rate': 1e-3,
            'max_replay_buffer_size': 1000
        }
        
        agent = BCAgent(env, agent_params)
        
        # First add some data to buffer
        paths = [{
            'observation': np.random.randn(5, 3).astype(np.float32),
            'action': np.random.randn(5, 2).astype(np.float32),
            'reward': np.random.randn(5).astype(np.float32),
            'next_observation': np.random.randn(5, 3).astype(np.float32),
            'terminal': np.zeros(5).astype(np.float32)
        }]
        agent.add_to_replay_buffer(paths)
        
        # Sample from buffer
        batch_size = 3
        ob_batch, ac_batch, re_batch, next_ob_batch, terminal_batch = agent.sample(batch_size)
        
        # Check shapes
        assert ob_batch.shape == (batch_size, 3)
        assert ac_batch.shape == (batch_size, 2)
        assert re_batch.shape == (batch_size,)
        assert next_ob_batch.shape == (batch_size, 3)
        assert terminal_batch.shape == (batch_size,)
        
    def test_sample_empty_buffer(self):
        """Test sampling from empty buffer should raise error"""
        env = self.create_mock_env(discrete=False)
        
        agent_params = {
            'ac_dim': 2,
            'ob_dim': 3,
            'n_layers': 1,
            'size': 8,
            'discrete': False,
            'learning_rate': 1e-3,
            'max_replay_buffer_size': 1000
        }
        
        agent = BCAgent(env, agent_params)
        
        # Try to sample from empty buffer
        # This should raise an assertion error in sample_random_data
        with pytest.raises(AssertionError):
            agent.sample(5)
            
    def test_save_method(self, tmp_path):
        """Test saving agent policy"""
        env = self.create_mock_env(discrete=False)
        
        agent_params = {
            'ac_dim': 2,
            'ob_dim': 3,
            'n_layers': 1,
            'size': 8,
            'discrete': False,
            'learning_rate': 1e-3,
            'max_replay_buffer_size': 1000
        }
        
        agent = BCAgent(env, agent_params)
        
        # Save policy
        save_path = tmp_path / "test_policy.pt"
        agent.save(save_path)
        
        assert save_path.exists()
        assert save_path.stat().st_size > 0
        
    def test_training_loop_integration(self):
        """Test integration of agent methods for training loop"""
        env = self.create_mock_env(discrete=False)
        
        agent_params = {
            'ac_dim': 2,
            'ob_dim': 4,
            'n_layers': 1,
            'size': 16,
            'discrete': False,
            'learning_rate': 1e-3,
            'max_replay_buffer_size': 10000
        }
        
        agent = BCAgent(env, agent_params)
        
        # Simulate a training iteration
        # 1. Collect data
        paths = [{
            'observation': np.random.randn(10, 4).astype(np.float32),
            'action': np.random.randn(10, 2).astype(np.float32),
            'reward': np.random.randn(10).astype(np.float32),
            'next_observation': np.random.randn(10, 4).astype(np.float32),
            'terminal': np.zeros(10).astype(np.float32)
        }]
        
        # 2. Add to replay buffer
        agent.add_to_replay_buffer(paths)
        
        # 3. Sample batch
        batch_size = 5
        ob_batch, ac_batch, re_batch, next_ob_batch, terminal_batch = agent.sample(batch_size)
        
        # 4. Train on batch
        log = agent.train(ob_batch, ac_batch, re_batch, next_ob_batch, terminal_batch)
        
        # Verify
        assert 'Training Loss' in log
        assert isinstance(log['Training Loss'], float)
        
    def test_agent_with_different_architectures(self):
        """Test agent with different network architectures"""
        env = self.create_mock_env(discrete=False)
        
        # Test with deeper network
        agent_params_deep = {
            'ac_dim': 3,
            'ob_dim': 6,
            'n_layers': 4,  # Deep network
            'size': 64,
            'discrete': False,
            'learning_rate': 1e-4,
            'max_replay_buffer_size': 10000
        }
        
        agent_deep = BCAgent(env, agent_params_deep)
        
        # Test with wider network
        agent_params_wide = {
            'ac_dim': 3,
            'ob_dim': 6,
            'n_layers': 1,
            'size': 256,  # Wide network
            'discrete': False,
            'learning_rate': 1e-4,
            'max_replay_buffer_size': 10000
        }
        
        agent_wide = BCAgent(env, agent_params_wide)
        
        # Both should create successfully
        assert agent_deep.actor is not None
        assert agent_wide.actor is not None
        
        # They should have different parameter counts
        params_deep = sum(p.numel() for p in agent_deep.actor.parameters())
        params_wide = sum(p.numel() for p in agent_wide.actor.parameters())
        
        assert params_deep != params_wide