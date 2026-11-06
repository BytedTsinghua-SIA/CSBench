"""
Unit tests for particle filter (Q9, Q10, Q11)
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add tracking directory to path
tracking_path = os.path.join(os.path.dirname(__file__), '..', 'tracking')
if tracking_path not in sys.path:
    sys.path.insert(0, tracking_path)

from inference import ParticleFilter, DiscreteDistribution
import busters


class TestParticleFilterInitialize:
    """Tests for Q9: ParticleFilter.initializeUniformly and getBeliefDistribution"""
    
    def test_initialize_uniformly_distributes_particles(self):
        """Test that particles are evenly distributed"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        filter_obj = ParticleFilter(ghost_agent, numParticles=100)
        filter_obj.legalPositions = [(1, 1), (2, 2), (3, 3), (4, 4)]
        
        game_state = MagicMock()
        filter_obj.initializeUniformly(game_state)
        
        assert len(filter_obj.particles) == 100
        # Check that all legal positions have particles
        particle_positions = set(filter_obj.particles)
        assert all(pos in particle_positions for pos in filter_obj.legalPositions)
    
    def test_initialize_uniformly_even_distribution(self):
        """Test that particles are evenly distributed across positions"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        filter_obj = ParticleFilter(ghost_agent, numParticles=12)
        filter_obj.legalPositions = [(1, 1), (2, 2), (3, 3)]
        
        game_state = MagicMock()
        filter_obj.initializeUniformly(game_state)
        
        # With 12 particles and 3 positions, each should have 4 particles
        counts = {pos: filter_obj.particles.count(pos) for pos in filter_obj.legalPositions}
        assert all(count == 4 for count in counts.values())
    
    def test_get_belief_distribution(self):
        """Test converting particles to belief distribution"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        filter_obj = ParticleFilter(ghost_agent, numParticles=10)
        filter_obj.particles = [(1, 1)] * 6 + [(2, 2)] * 4
        
        belief = filter_obj.getBeliefDistribution()
        
        assert isinstance(belief, DiscreteDistribution)
        assert belief[(1, 1)] == pytest.approx(0.6)
        assert belief[(2, 2)] == pytest.approx(0.4)
        assert sum(belief.values()) == pytest.approx(1.0)


class TestParticleFilterObserveUpdate:
    """Tests for Q10: ParticleFilter.observeUpdate"""
    
    def test_observe_update_resamples(self):
        """Test that observeUpdate resamples particles"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        filter_obj = ParticleFilter(ghost_agent, numParticles=10)
        filter_obj.legalPositions = [(1, 1), (2, 2)]
        filter_obj.particles = [(1, 1)] * 5 + [(2, 2)] * 5
        
        game_state = MagicMock()
        game_state.getPacmanPosition.return_value = (0, 0)
        filter_obj.getJailPosition = lambda: (10, 10)
        
        with patch.object(filter_obj, 'getObservationProb') as mock_obs:
            mock_obs.side_effect = lambda obs, pac, ghost, jail: 0.9 if ghost == (1, 1) else 0.1
            
            filter_obj.observeUpdate(5, game_state)
            
            # After resampling, more particles should be at (1, 1)
            assert len(filter_obj.particles) == 10
            assert filter_obj.particles.count((1, 1)) >= 5
    
    def test_observe_update_reinitializes_on_zero_weights(self):
        """Test that observeUpdate reinitializes when all weights are zero"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        filter_obj = ParticleFilter(ghost_agent, numParticles=10)
        filter_obj.legalPositions = [(1, 1), (2, 2)]
        filter_obj.particles = [(1, 1)] * 10
        
        game_state = MagicMock()
        game_state.getPacmanPosition.return_value = (0, 0)
        filter_obj.getJailPosition = lambda: (10, 10)
        
        with patch.object(filter_obj, 'getObservationProb', return_value=0.0):
            with patch.object(filter_obj, 'initializeUniformly') as mock_init:
                filter_obj.observeUpdate(5, game_state)
                mock_init.assert_called_once()


class TestParticleFilterElapseTime:
    """Tests for Q11: ParticleFilter.elapseTime"""
    
    def test_elapse_time_samples_new_positions(self):
        """Test that elapseTime samples new positions for each particle"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        filter_obj = ParticleFilter(ghost_agent, numParticles=5)
        filter_obj.particles = [(1, 1)] * 5
        
        game_state = MagicMock()
        
        def mock_get_position_dist(game_state, old_pos):
            dist = DiscreteDistribution()
            dist[(2, 2)] = 1.0
            return dist
        
        filter_obj.getPositionDistribution = mock_get_position_dist
        
        filter_obj.elapseTime(game_state)
        
        # All particles should move to (2, 2)
        assert all(particle == (2, 2) for particle in filter_obj.particles)
        assert len(filter_obj.particles) == 5
    
    def test_elapse_time_preserves_particle_count(self):
        """Test that elapseTime preserves number of particles"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        filter_obj = ParticleFilter(ghost_agent, numParticles=10)
        filter_obj.particles = [(1, 1)] * 10
        
        game_state = MagicMock()
        
        def mock_get_position_dist(game_state, old_pos):
            dist = DiscreteDistribution()
            dist[old_pos] = 1.0
            return dist
        
        filter_obj.getPositionDistribution = mock_get_position_dist
        
        filter_obj.elapseTime(game_state)
        
        assert len(filter_obj.particles) == 10

