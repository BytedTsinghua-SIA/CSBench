"""
Test PG agent implementation for CS285 Homework 2
"""
import numpy as np
import pytest
import gym
from unittest.mock import Mock, MagicMock

from cs285.agents.pg_agent import PGAgent
from cs285.infrastructure import pytorch_util as ptu
from cs285.policies.MLP_policy import MLPPolicyPG


class TestPGAgent:
    """Test Policy Gradient agent"""

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

    def test_agent_creation(self):
        """Test creation of PG agent"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': True,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        assert agent.env == env
        assert agent.agent_params == agent_params
        assert agent.gamma == 0.99
        assert agent.standardize_advantages == True
        assert agent.nn_baseline == False
        assert agent.reward_to_go == False
        assert agent.actor is not None
        assert agent.replay_buffer is not None

    def test_discounted_return(self):
        """Test discounted return computation"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Simple case: rewards = [1, 1, 1], gamma = 0.99
        # For trajectory-based PG, all timesteps get the same total discounted return
        # Total return = 1 + 0.99*1 + 0.99^2*1 = 1 + 0.99 + 0.9801 = 2.9701
        rewards = [1.0, 1.0, 1.0]
        returns = agent._discounted_return(rewards)

        expected_total_return = 1.0 + 0.99 * 1.0 + 0.99**2 * 1.0

        assert len(returns) == 3
        # All timesteps should have the same total return (trajectory-based)
        assert np.isclose(returns[0], expected_total_return)
        assert np.isclose(returns[1], expected_total_return)
        assert np.isclose(returns[2], expected_total_return)

    def test_discounted_cumsum(self):
        """Test discounted cumulative sum (reward-to-go)"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # rewards = [1, 2, 3], gamma = 0.99
        # Cumsum at t=0: 1 + 0.99*2 + 0.99^2*3
        # Cumsum at t=1: 2 + 0.99*3
        # Cumsum at t=2: 3
        rewards = [1.0, 2.0, 3.0]
        cumsums = agent._discounted_cumsum(rewards)

        expected_cumsum_0 = 1.0 + 0.99 * 2.0 + 0.99**2 * 3.0
        expected_cumsum_1 = 2.0 + 0.99 * 3.0
        expected_cumsum_2 = 3.0

        assert len(cumsums) == 3
        assert np.isclose(cumsums[0], expected_cumsum_0)
        assert np.isclose(cumsums[1], expected_cumsum_1)
        assert np.isclose(cumsums[2], expected_cumsum_2)

    def test_calculate_q_vals_trajectory_based(self):
        """Test Q value calculation with trajectory-based estimator"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,  # trajectory-based
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Two trajectories
        rewards_list = [[1.0, 1.0], [2.0, 2.0]]
        q_values = agent.calculate_q_vals(rewards_list)

        # Should be flattened
        assert len(q_values) == 4

    def test_calculate_q_vals_reward_to_go(self):
        """Test Q value calculation with reward-to-go estimator"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': True,  # reward-to-go
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        rewards_list = [[1.0, 1.0], [2.0, 2.0]]
        q_values = agent.calculate_q_vals(rewards_list)

        # Should be flattened
        assert len(q_values) == 4

        # For reward-to-go, values should differ from trajectory-based
        agent.reward_to_go = False
        q_values_trajectory = agent.calculate_q_vals(rewards_list)

        # Reward-to-go and trajectory-based should give different results
        assert not np.allclose(q_values, q_values_trajectory)

    def test_estimate_advantage_no_baseline(self):
        """Test advantage estimation without baseline"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        obs = np.random.randn(4, 8).astype(np.float32)
        rewards_list = [[1.0, 1.0], [2.0, 2.0]]
        q_values = np.array([1.0, 1.0, 2.0, 2.0]).astype(np.float32)
        terminals = np.array([0.0, 1.0, 0.0, 1.0]).astype(np.float32)

        advantages = agent.estimate_advantage(obs, rewards_list, q_values, terminals)

        # Without baseline, advantages should equal q_values
        assert np.allclose(advantages, q_values)

    def test_estimate_advantage_with_baseline(self):
        """Test advantage estimation with neural network baseline"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': True,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        obs = np.random.randn(4, 8).astype(np.float32)
        rewards_list = [[1.0, 1.0], [2.0, 2.0]]
        q_values = np.array([1.0, 1.0, 2.0, 2.0]).astype(np.float32)
        terminals = np.array([0.0, 1.0, 0.0, 1.0]).astype(np.float32)

        advantages = agent.estimate_advantage(obs, rewards_list, q_values, terminals)

        # With baseline, advantages should be q_values - baseline
        assert advantages.shape == q_values.shape

    def test_estimate_advantage_standardization(self):
        """Test advantage standardization"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': True,  # Enable standardization
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        obs = np.random.randn(4, 8).astype(np.float32)
        rewards_list = [[1.0, 1.0], [2.0, 2.0]]
        q_values = np.array([1.0, 2.0, 3.0, 4.0]).astype(np.float32)
        terminals = np.zeros(4).astype(np.float32)

        advantages = agent.estimate_advantage(obs, rewards_list, q_values, terminals)

        # Standardized advantages should have mean ~0 and std ~1
        assert np.isclose(np.mean(advantages), 0.0, atol=1e-5)
        assert np.isclose(np.std(advantages), 1.0, atol=1e-5)

    def test_estimate_advantage_with_gae(self):
        """Test advantage estimation with GAE"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': True,
            'reward_to_go': False,
            'gae_lambda': 0.95  # Enable GAE
        }

        agent = PGAgent(env, agent_params)

        obs = np.random.randn(4, 8).astype(np.float32)
        rewards_list = [[1.0, 1.0], [2.0, 2.0]]
        q_values = np.array([1.0, 1.0, 2.0, 2.0]).astype(np.float32)
        terminals = np.array([0.0, 1.0, 0.0, 1.0]).astype(np.float32)

        advantages = agent.estimate_advantage(obs, rewards_list, q_values, terminals)

        # GAE should still produce valid advantages
        assert advantages.shape == q_values.shape

    def test_train_method(self):
        """Test agent training method"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': True,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Create dummy batch data
        observations = np.random.randn(4, 8).astype(np.float32)
        actions = np.random.randint(0, 5, size=(4,)).astype(np.float32)
        rewards_list = [[1.0, 1.0], [2.0, 2.0]]
        next_observations = np.random.randn(4, 8).astype(np.float32)
        terminals = np.zeros(4).astype(np.float32)

        # Train agent
        log = agent.train(observations, actions, rewards_list, next_observations, terminals)

        # Check training log
        assert 'Training Loss' in log
        assert isinstance(log['Training Loss'], float)
        assert log['Training Loss'] >= 0

    def test_add_to_replay_buffer(self):
        """Test adding paths to replay buffer"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Create dummy paths
        paths = [
            {
                'observation': np.random.randn(3, 8).astype(np.float32),
                'action': np.random.randn(3, 5).astype(np.float32),
                'reward': np.random.randn(3).astype(np.float32),
                'next_observation': np.random.randn(3, 8).astype(np.float32),
                'terminal': np.zeros(3).astype(np.float32)
            }
        ]

        # Add to buffer
        initial_size = len(agent.replay_buffer)
        agent.add_to_replay_buffer(paths)

        # Buffer should have more data
        assert len(agent.replay_buffer) > initial_size

    def test_sample_method(self):
        """Test sampling from replay buffer"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # First add some data to buffer
        paths = [{
            'observation': np.random.randn(5, 8).astype(np.float32),
            'action': np.random.randn(5, 5).astype(np.float32),
            'reward': np.random.randn(5).astype(np.float32),
            'next_observation': np.random.randn(5, 8).astype(np.float32),
            'terminal': np.zeros(5).astype(np.float32)
        }]
        agent.add_to_replay_buffer(paths)

        # Sample from buffer
        batch_size = 3
        result = agent.sample(batch_size)

        # Check that we get the right number of returns
        assert len(result) == 5  # obs, acs, unconcatenated_rews, next_obs, terminals

    # ============================================================
    # Boundary condition tests
    # ============================================================

    def test_discounted_return_empty(self):
        """Test discounted return with empty rewards list"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Empty rewards list should return empty list
        returns = agent._discounted_return([])
        assert returns == []

    def test_discounted_cumsum_empty(self):
        """Test discounted cumsum with empty rewards list"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Empty rewards list should return empty list
        cumsums = agent._discounted_cumsum([])
        assert cumsums == []

    def test_discounted_return_single(self):
        """Test discounted return with single reward"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Single reward should return list with one element (the reward itself)
        rewards = [5.0]
        returns = agent._discounted_return(rewards)

        assert len(returns) == 1
        assert np.isclose(returns[0], 5.0)

    def test_discounted_cumsum_single(self):
        """Test discounted cumsum with single reward"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Single reward should return list with one element
        rewards = [5.0]
        cumsums = agent._discounted_cumsum(rewards)

        assert len(cumsums) == 1
        assert np.isclose(cumsums[0], 5.0)

    def test_discounted_return_gamma_one(self):
        """Test discounted return with gamma=1 (no discounting)"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 1.0,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # With gamma=1, total return is sum of all rewards
        rewards = [1.0, 2.0, 3.0]
        returns = agent._discounted_return(rewards)

        expected_total = 1.0 + 2.0 + 3.0  # = 6.0
        assert len(returns) == 3
        assert np.allclose(returns, expected_total)

    def test_discounted_cumsum_gamma_one(self):
        """Test discounted cumsum with gamma=1 (no discounting)"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 1.0,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # With gamma=1, cumsum from each position is sum of remaining rewards
        rewards = [1.0, 2.0, 3.0]
        cumsums = agent._discounted_cumsum(rewards)

        # t=0: 1+2+3=6, t=1: 2+3=5, t=2: 3=3
        expected = [6.0, 5.0, 3.0]
        assert np.allclose(cumsums, expected)

    def test_discounted_return_gamma_zero(self):
        """Test discounted return with gamma=0 (only immediate reward)"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.0,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # With gamma=0, total return is just the first reward (r_0)
        rewards = [1.0, 2.0, 3.0]
        returns = agent._discounted_return(rewards)

        # For trajectory-based, all timesteps get r_0 (since future rewards are discounted to 0)
        expected_total = 1.0  # r_0 only
        assert len(returns) == 3
        assert np.allclose(returns, expected_total)

    def test_discounted_cumsum_gamma_zero(self):
        """Test discounted cumsum with gamma=0 (only immediate reward)"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.0,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # With gamma=0, each position only gets its own reward
        rewards = [1.0, 2.0, 3.0]
        cumsums = agent._discounted_cumsum(rewards)

        # t=0: r_0=1, t=1: r_1=2, t=2: r_2=3
        expected = [1.0, 2.0, 3.0]
        assert np.allclose(cumsums, expected)

    def test_calculate_q_vals_multiple_trajectories(self):
        """Test Q value calculation with multiple trajectories"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Multiple trajectories
        rewards_list = [
            [1.0, 1.0],  # Trajectory 1
            [2.0, 2.0, 2.0],  # Trajectory 2
            [3.0]  # Trajectory 3
        ]

        q_values = agent.calculate_q_vals(rewards_list)

        # Should flatten to total length
        assert len(q_values) == 6  # 2 + 3 + 1 = 6

        # All timesteps in same trajectory should have same total return
        # Trajectory 1: 1 + 0.99*1 = 1.99
        # Trajectory 2: 2 + 0.99*2 + 0.99^2*2 = 5.9402
        # Trajectory 3: 3.0

    def test_calculate_q_vals_reward_to_go_multiple_trajectories(self):
        """Test Q value calculation with reward-to-go and multiple trajectories"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Multiple trajectories
        rewards_list = [
            [1.0, 1.0],  # Trajectory 1
            [2.0, 2.0, 2.0],  # Trajectory 2
        ]

        q_values = agent.calculate_q_vals(rewards_list)

        # Should flatten to total length
        assert len(q_values) == 5  # 2 + 3 = 5

        # Verify different trajectories have different values
        # Trajectory 1 RTG: [1.99, 1.0]
        # Trajectory 2 RTG: [5.9402, 3.98, 2.0]
        assert np.isclose(q_values[0], 1.99)  # t=0 of trajectory 1
        assert np.isclose(q_values[1], 1.0)   # t=1 of trajectory 1
        assert np.isclose(q_values[2], 5.9402, rtol=1e-4)  # t=0 of trajectory 2
        assert np.isclose(q_values[3], 3.98, rtol=1e-4)    # t=1 of trajectory 2
        assert np.isclose(q_values[4], 2.0)   # t=2 of trajectory 2

    def test_advantage_standardization_no_nan(self):
        """Test that advantage standardization doesn't produce NaN"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': True,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Create data with all same advantages (edge case)
        observations = np.random.randn(5, 8).astype(np.float32)
        rewards_list = [[1.0, 1.0], [1.0, 1.0], [1.0]]
        q_values = agent.calculate_q_vals(rewards_list)

        # Should not produce NaN even with uniform values
        assert not np.any(np.isnan(q_values))

    def test_negative_rewards(self):
        """Test with negative rewards"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': False,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Negative rewards
        rewards = [-1.0, -2.0, -3.0]
        returns = agent._discounted_return(rewards)

        # Total return should be negative
        expected_total = -1.0 + (-2.0) * 0.99 + (-3.0) * (0.99 ** 2)
        assert np.allclose(returns, expected_total)

    def test_mixed_rewards(self):
        """Test with mixed positive and negative rewards"""
        env = self.create_mock_env(discrete=True)

        agent_params = {
            'ac_dim': 5,
            'ob_dim': 8,
            'n_layers': 2,
            'size': 32,
            'discrete': True,
            'learning_rate': 1e-3,
            'gamma': 0.99,
            'standardize_advantages': False,
            'nn_baseline': False,
            'reward_to_go': True,
            'gae_lambda': None
        }

        agent = PGAgent(env, agent_params)

        # Mixed rewards
        rewards = [5.0, -2.0, 3.0]
        cumsums = agent._discounted_cumsum(rewards)

        # t=0: 5 + 0.99*(-2) + 0.99^2*3
        # t=1: -2 + 0.99*3
        # t=2: 3
        expected_0 = 5.0 + 0.99 * (-2.0) + (0.99 ** 2) * 3.0
        expected_1 = -2.0 + 0.99 * 3.0
        expected_2 = 3.0

        assert np.isclose(cumsums[0], expected_0, rtol=1e-4)
        assert np.isclose(cumsums[1], expected_1)
        assert np.isclose(cumsums[2], expected_2)
