"""
Test replay buffer implementation for CS285 Homework 2
"""
import numpy as np
import pytest

from cs285.infrastructure.replay_buffer import ReplayBuffer
from cs285.infrastructure.utils import Path


class TestReplayBuffer:
    """Test replay buffer functionality"""

    def test_empty_buffer(self):
        """Test empty buffer properties"""
        buffer = ReplayBuffer(max_size=1000)

        assert len(buffer) == 0
        assert buffer.obs is None
        assert buffer.acs is None
        assert buffer.concatenated_rews is None
        assert buffer.unconcatenated_rews is None
        assert buffer.next_obs is None
        assert buffer.terminals is None

    def create_dummy_path(self, length=5):
        """Create a dummy path for testing"""
        return Path(
            obs=np.random.randn(length, 3).astype(np.float32),
            image_obs=[],
            acs=np.random.randn(length, 2).astype(np.float32),
            rewards=np.random.randn(length).astype(np.float32),
            next_obs=np.random.randn(length, 3).astype(np.float32),
            terminals=np.zeros(length).astype(np.float32)
        )

    def test_add_single_rollout(self):
        """Test adding a single rollout to buffer"""
        buffer = ReplayBuffer(max_size=1000)
        path = self.create_dummy_path(length=3)

        buffer.add_rollouts([path])

        assert len(buffer) == 3
        assert buffer.obs.shape == (3, 3)
        assert buffer.acs.shape == (3, 2)
        assert buffer.concatenated_rews.shape == (3,)
        assert buffer.next_obs.shape == (3, 3)
        assert buffer.terminals.shape == (3,)

    def test_add_multiple_rollouts(self):
        """Test adding multiple rollouts to buffer"""
        buffer = ReplayBuffer(max_size=1000)
        paths = [
            self.create_dummy_path(length=2),
            self.create_dummy_path(length=3)
        ]

        buffer.add_rollouts(paths)

        assert len(buffer) == 5
        assert buffer.obs.shape == (5, 3)
        assert buffer.acs.shape == (5, 2)

    def test_max_size(self):
        """Test that buffer respects max size"""
        buffer = ReplayBuffer(max_size=5)

        # Add more data than max size
        paths = [
            self.create_dummy_path(length=3),
            self.create_dummy_path(length=3)  # Total 6 > max_size 5
        ]

        buffer.add_rollouts(paths)

        # Should be truncated to max_size
        assert len(buffer) == 5
        assert buffer.obs.shape[0] == 5

    def test_sample_recent_data(self):
        """Test sampling recent data from buffer"""
        buffer = ReplayBuffer(max_size=1000)

        # Add some data
        paths = [
            self.create_dummy_path(length=4),
            self.create_dummy_path(length=4)
        ]
        buffer.add_rollouts(paths)

        # Sample recent data
        batch_size = 3
        obs, acs, unconcatenated_rews, next_obs, terminals = buffer.sample_recent_data(batch_size, concat_rew=False)

        assert obs.shape == (batch_size, 3)
        assert acs.shape == (batch_size, 2)
        assert len(unconcatenated_rews) >= 1  # At least one trajectory
        assert next_obs.shape == (batch_size, 3)
        assert terminals.shape == (batch_size,)

    def test_sample_random_data(self):
        """Test sampling random data from buffer"""
        buffer = ReplayBuffer(max_size=1000)

        # Add some data
        paths = [
            self.create_dummy_path(length=10),
            self.create_dummy_path(length=10)
        ]
        buffer.add_rollouts(paths)

        # Sample random data
        batch_size = 5
        obs, acs, rews, next_obs, terminals = buffer.sample_random_data(batch_size)

        assert obs.shape == (batch_size, 3)
        assert acs.shape == (batch_size, 2)
        assert rews.shape == (batch_size,)
        assert next_obs.shape == (batch_size, 3)
        assert terminals.shape == (batch_size,)

    def test_sample_random_data_small_batch(self):
        """Test sampling when batch size > buffer size"""
        buffer = ReplayBuffer(max_size=1000)

        # Add small amount of data
        path = self.create_dummy_path(length=3)
        buffer.add_rollouts([path])

        # Try to sample more than available
        batch_size = 5
        obs, acs, rews, next_obs, terminals = buffer.sample_random_data(batch_size)

        # Should return all available data (3 samples)
        assert obs.shape[0] == 3
        assert acs.shape[0] == 3

    def test_buffer_length(self):
        """Test __len__ method"""
        buffer = ReplayBuffer(max_size=1000)

        # Empty buffer
        assert len(buffer) == 0

        # Add some data
        path = self.create_dummy_path(length=7)
        buffer.add_rollouts([path])

        assert len(buffer) == 7

        # Add more data
        another_path = self.create_dummy_path(length=5)
        buffer.add_rollouts([another_path])

        assert len(buffer) == 12

    def test_concatenation_consistency(self):
        """Test that concatenated arrays have consistent shapes"""
        buffer = ReplayBuffer(max_size=1000)

        # Add multiple rollouts of different lengths
        paths = [
            self.create_dummy_path(length=2),
            self.create_dummy_path(length=4),
            self.create_dummy_path(length=3)
        ]
        buffer.add_rollouts(paths)

        # All arrays should have same first dimension
        assert buffer.obs.shape[0] == buffer.acs.shape[0]
        assert buffer.acs.shape[0] == buffer.concatenated_rews.shape[0]
        assert buffer.concatenated_rews.shape[0] == buffer.next_obs.shape[0]
        assert buffer.next_obs.shape[0] == buffer.terminals.shape[0]

        # Total should be sum of path lengths
        total_length = 2 + 4 + 3
        assert buffer.obs.shape[0] == total_length

    def test_paths_storage(self):
        """Test that paths are stored in buffer"""
        buffer = ReplayBuffer(max_size=1000)

        paths = [
            self.create_dummy_path(length=3),
            self.create_dummy_path(length=2)
        ]

        buffer.add_rollouts(paths)

        # Check that paths are stored
        assert len(buffer.paths) == 2

    def test_sample_recent_rollouts(self):
        """Test sampling recent rollouts"""
        buffer = ReplayBuffer(max_size=1000)

        # Add some paths
        for _ in range(5):
            buffer.add_rollouts([self.create_dummy_path(length=3)])

        # Sample recent rollouts
        rollouts = buffer.sample_recent_rollouts(2)

        assert len(rollouts) == 2

    def test_sample_random_rollouts(self):
        """Test sampling random rollouts"""
        buffer = ReplayBuffer(max_size=1000)

        # Add some paths
        for _ in range(5):
            buffer.add_rollouts([self.create_dummy_path(length=3)])

        # Sample random rollouts
        rollouts = buffer.sample_random_rollouts(2)

        assert len(rollouts) == 2
