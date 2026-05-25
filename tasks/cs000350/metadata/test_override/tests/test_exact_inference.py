"""
Unit tests for exact inference (Q6, Q7)
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add tracking directory to path
tracking_path = os.path.join(os.path.dirname(__file__), '..', 'tracking')
if tracking_path not in sys.path:
    sys.path.insert(0, tracking_path)

from inference import ExactInference, DiscreteDistribution
import busters


class TestExactInferenceObserveUpdate:
    """Tests for Q6: ExactInference.observeUpdate"""
    
    def test_observe_update_basic(self):
        """Test basic observation update"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        inference = ExactInference(ghost_agent)
        inference.legalPositions = [(1, 1), (2, 2), (3, 3)]
        inference.allPositions = inference.legalPositions + [(0, 0)]
        inference.beliefs = DiscreteDistribution()
        for pos in inference.legalPositions:
            inference.beliefs[pos] = 1.0 / len(inference.legalPositions)
        
        game_state = MagicMock()
        game_state.getPacmanPosition.return_value = (0, 0)
        
        with patch.object(inference, 'getObservationProb') as mock_obs:
            mock_obs.side_effect = lambda obs, pac, ghost, jail: 0.5 if ghost == (1, 1) else 0.1
            
            inference.observeUpdate(5, game_state)
            
            # Belief at (1, 1) should be higher due to higher observation probability
            assert inference.beliefs[(1, 1)] > inference.beliefs[(2, 2)]
            assert sum(inference.beliefs.values()) == pytest.approx(1.0)
    
    def test_observe_update_normalizes(self):
        """Test that observeUpdate normalizes beliefs"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        inference = ExactInference(ghost_agent)
        inference.legalPositions = [(1, 1), (2, 2)]
        inference.allPositions = inference.legalPositions + [(0, 0)]
        inference.beliefs = DiscreteDistribution()
        inference.beliefs[(1, 1)] = 0.3
        inference.beliefs[(2, 2)] = 0.7
        
        game_state = MagicMock()
        game_state.getPacmanPosition.return_value = (0, 0)
        
        with patch.object(inference, 'getObservationProb', return_value=0.5):
            inference.observeUpdate(5, game_state)
            
            total = sum(inference.beliefs.values())
            assert total == pytest.approx(1.0)


class TestExactInferenceElapseTime:
    """Tests for Q7: ExactInference.elapseTime"""
    
    def test_elapse_time_basic(self):
        """Test basic time elapse"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        inference = ExactInference(ghost_agent)
        inference.legalPositions = [(1, 1), (2, 2)]
        inference.allPositions = inference.legalPositions + [(0, 0)]
        inference.beliefs = DiscreteDistribution()
        inference.beliefs[(1, 1)] = 1.0
        inference.beliefs[(2, 2)] = 0.0
        
        game_state = MagicMock()
        
        def mock_get_position_dist(game_state, old_pos):
            dist = DiscreteDistribution()
            if old_pos == (1, 1):
                dist[(2, 2)] = 0.5
                dist[(1, 1)] = 0.5
            else:
                dist[old_pos] = 1.0
            return dist
        
        inference.getPositionDistribution = mock_get_position_dist
        
        inference.elapseTime(game_state)
        
        # Belief should spread from (1, 1) to (2, 2)
        assert inference.beliefs[(2, 2)] > 0
        assert sum(inference.beliefs.values()) == pytest.approx(1.0)
    
    def test_elapse_time_preserves_total_probability(self):
        """Test that elapseTime preserves total probability"""
        ghost_agent = MagicMock()
        ghost_agent.index = 1
        inference = ExactInference(ghost_agent)
        inference.legalPositions = [(1, 1), (2, 2), (3, 3)]
        inference.allPositions = inference.legalPositions + [(0, 0)]
        inference.beliefs = DiscreteDistribution()
        for pos in inference.legalPositions:
            inference.beliefs[pos] = 1.0 / len(inference.legalPositions)
        
        game_state = MagicMock()
        
        def mock_get_position_dist(game_state, old_pos):
            dist = DiscreteDistribution()
            dist[old_pos] = 0.5
            # Add some transitions
            for other_pos in inference.legalPositions:
                if other_pos != old_pos:
                    dist[other_pos] = 0.5 / (len(inference.legalPositions) - 1)
            return dist
        
        inference.getPositionDistribution = mock_get_position_dist
        
        inference.elapseTime(game_state)
        
        total = sum(inference.beliefs.values())
        assert total == pytest.approx(1.0)

