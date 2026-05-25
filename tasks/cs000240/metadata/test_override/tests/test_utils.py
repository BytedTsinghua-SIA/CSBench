"""
Test utility functions for CS285 Homework 2
"""
import numpy as np
import pytest

from cs285.infrastructure.utils import (
    sample_trajectory,
    sample_trajectories,
    sample_n_trajectories,
    Path,
    convert_listofrollouts,
    get_pathlength,
    normalize,
    unnormalize
)


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
            actions = np.random.randn(batch_size, self.action_dim).astype(np.float32)

        return actions


class MockEnv:
    """Mock environment for testing"""
    def __init__(self, obs_dim=4, action_dim=2, discrete=False, max_steps=10):
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.discrete = discrete
        self.max_steps = max_steps
        self.step_count = 0

    def reset(self):
        self.step_count = 0
        obs = np.random.randn(self.obs_dim).astype(np.float32)
        return obs

    def step(self, action):
        self.step_count += 1
        obs = np.random.randn(self.obs_dim).astype(np.float32)
        reward = 1.0
        terminated = self.step_count >= self.max_steps
        truncated = False
        info = {}

        return obs, reward, terminated, truncated, info

    def render(self):
        return np.zeros((64, 64, 3), dtype=np.uint8)


class TestPath:
    """Test Path data structure"""

    def test_path_creation(self):
        """Test Path creation with arrays"""
        obs = np.random.randn(5, 3).astype(np.float32)
        image_obs = []
        acs = np.random.randn(5, 2).astype(np.float32)
        rewards = np.random.randn(5).astype(np.float32)
        next_obs = np.random.randn(5, 3).astype(np.float32)
        terminals = np.array([0, 0, 0, 1, 0], dtype=np.float32)

        path = Path(obs, image_obs, acs, rewards, next_obs, terminals)

        assert 'observation' in path
        assert 'action' in path
        assert 'reward' in path
        assert 'next_observation' in path
        assert 'terminal' in path

        assert path['observation'].shape == (5, 3)
        assert path['action'].shape == (5, 2)
        assert path['reward'].shape == (5,)
        assert path['next_observation'].shape == (5, 3)
        assert path['terminal'].shape == (5,)

    def test_path_with_images(self):
        """Test Path creation with image observations"""
        obs = np.random.randn(3, 4).astype(np.float32)
        image_obs = [np.zeros((64, 64, 3), dtype=np.uint8) for _ in range(3)]
        acs = np.random.randn(3, 2).astype(np.float32)
        rewards = np.random.randn(3).astype(np.float32)
        next_obs = np.random.randn(3, 4).astype(np.float32)
        terminals = np.zeros(3).astype(np.float32)

        path = Path(obs, image_obs, acs, rewards, next_obs, terminals)

        assert path['image_obs'].shape == (3, 64, 64, 3)


class TestConvertListOfRollouts:
    """Test convert_listofrollouts function"""

    def test_convert_single_rollout(self):
        """Test conversion of single rollout"""
        path = Path(
            obs=np.random.randn(5, 4).astype(np.float32),
            image_obs=[],
            acs=np.random.randn(5, 2).astype(np.float32),
            rewards=np.random.randn(5).astype(np.float32),
            next_obs=np.random.randn(5, 4).astype(np.float32),
            terminals=np.zeros(5).astype(np.float32)
        )

        obs, acs, next_obs, terminals, concat_rews, unconcat_rews = convert_listofrollouts([path])

        assert obs.shape == (5, 4)
        assert acs.shape == (5, 2)
        assert next_obs.shape == (5, 4)
        assert terminals.shape == (5,)
        assert concat_rews.shape == (5,)
        assert len(unconcat_rews) == 1

    def test_convert_multiple_rollouts(self):
        """Test conversion of multiple rollouts"""
        paths = []
        for length in [3, 5, 2]:
            path = Path(
                obs=np.random.randn(length, 4).astype(np.float32),
                image_obs=[],
                acs=np.random.randn(length, 2).astype(np.float32),
                rewards=np.random.randn(length).astype(np.float32),
                next_obs=np.random.randn(length, 4).astype(np.float32),
                terminals=np.zeros(length).astype(np.float32)
            )
            paths.append(path)

        obs, acs, next_obs, terminals, concat_rews, unconcat_rews = convert_listofrollouts(paths)

        assert obs.shape == (10, 4)  # 3 + 5 + 2
        assert acs.shape == (10, 2)
        assert len(unconcat_rews) == 3


class TestGetPathLength:
    """Test get_pathlength function"""

    def test_path_length(self):
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


class TestSampleTrajectory:
    """Test trajectory sampling functions"""

    def test_sample_trajectory(self):
        """Test single trajectory sampling"""
        env = MockEnv(obs_dim=5, action_dim=2, max_steps=10)
        policy = MockPolicy(action_dim=2)

        path = sample_trajectory(env, policy, max_path_length=20, render=False)

        assert 'observation' in path
        assert 'action' in path
        assert 'reward' in path
        assert 'next_observation' in path
        assert 'terminal' in path

        # Path should have at most max_steps (10)
        path_length = get_pathlength(path)
        assert path_length <= 10
        assert path_length > 0

    def test_sample_trajectory_early_termination(self):
        """Test trajectory that terminates early"""
        env = MockEnv(obs_dim=3, action_dim=1, max_steps=3)  # Very short max steps
        policy = MockPolicy(action_dim=1)

        path = sample_trajectory(env, policy, max_path_length=100, render=False)

        # Should terminate at max_steps (3)
        path_length = get_pathlength(path)
        assert path_length == 3

    def test_sample_trajectories(self):
        """Test batch trajectory sampling"""
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

    def test_sample_n_trajectories(self):
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


class TestNormalize:
    """Test normalization utilities"""

    def test_normalize(self):
        """Test normalize function"""
        data = np.array([1, 2, 3, 4, 5], dtype=np.float32)
        mean = 3.0
        std = 2.0

        normalized = normalize(data, mean, std)

        expected = (data - mean) / (std + 1e-8)
        assert np.allclose(normalized, expected)

    def test_normalize_with_eps(self):
        """Test normalize with small std (should use eps)"""
        data = np.array([1, 2, 3], dtype=np.float32)
        mean = 2.0
        std = 0.0  # Zero std

        normalized = normalize(data, mean, std, eps=1e-8)

        # Should not divide by zero
        assert not np.any(np.isnan(normalized))

    def test_unnormalize(self):
        """Test unnormalize function"""
        data = np.array([0, 0.5, 1], dtype=np.float32)
        mean = 3.0
        std = 2.0

        unnormalized = unnormalize(data, mean, std)

        expected = data * std + mean
        assert np.allclose(unnormalized, expected)
