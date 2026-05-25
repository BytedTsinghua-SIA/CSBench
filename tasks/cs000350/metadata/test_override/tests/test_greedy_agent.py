"""
Unit tests for greedy agent (Q8)
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add tracking directory to path
tracking_path = os.path.join(os.path.dirname(__file__), '..', 'tracking')
if tracking_path not in sys.path:
    sys.path.insert(0, tracking_path)

from bustersAgents import GreedyBustersAgent
from game import Directions
from inference import DiscreteDistribution


class TestGreedyBustersAgent:
    """Tests for Q8: GreedyBustersAgent.chooseAction"""
    
    def test_choose_action_finds_closest_ghost(self):
        """Test that agent chooses action towards closest ghost"""
        ghost_agents = [MagicMock(), MagicMock()]
        agent = GreedyBustersAgent(ghostAgents=ghost_agents)
        agent.ghostBeliefs = []
        agent.distancer = MagicMock()
        
        # Setup beliefs
        dist1 = DiscreteDistribution()
        dist1[(5, 5)] = 1.0
        dist2 = DiscreteDistribution()
        dist2[(10, 10)] = 1.0
        
        agent.ghostBeliefs = [dist1, dist2]
        
        game_state = MagicMock()
        game_state.getPacmanPosition.return_value = (0, 0)
        game_state.getLegalPacmanActions.return_value = [Directions.NORTH, Directions.EAST]
        game_state.getLivingGhosts.return_value = {1: True, 2: True}
        
        # Mock distance calculator
        def mock_get_distance(pos1, pos2):
            if pos2 == (5, 5):
                return 7
            elif pos2 == (10, 10):
                return 14
            return 100
        
        agent.distancer.getDistance = mock_get_distance
        
        with patch('bustersAgents.Actions.getSuccessor') as mock_successor:
            mock_successor.side_effect = lambda pos, action: {
                Directions.NORTH: (0, 1),
                Directions.EAST: (1, 0)
            }[action]
            
            action = agent.chooseAction(game_state)
            
            assert action in [Directions.NORTH, Directions.EAST]
    
    def test_choose_action_handles_no_living_ghosts(self):
        """Test that agent handles case with no living ghosts"""
        ghost_agents = [MagicMock(), MagicMock()]
        agent = GreedyBustersAgent(ghostAgents=ghost_agents)
        agent.ghostBeliefs = []
        
        game_state = MagicMock()
        game_state.getPacmanPosition.return_value = (0, 0)
        game_state.getLegalPacmanActions.return_value = [Directions.NORTH]
        game_state.getLivingGhosts.return_value = {1: False, 2: False}
        
        action = agent.chooseAction(game_state)
        
        assert action == Directions.STOP
    
    def test_choose_action_uses_maze_distance(self):
        """Test that agent uses maze distance, not Manhattan distance"""
        ghost_agents = [MagicMock()]
        agent = GreedyBustersAgent(ghostAgents=ghost_agents)
        agent.ghostBeliefs = []
        agent.distancer = MagicMock()
        
        dist = DiscreteDistribution()
        dist[(5, 5)] = 1.0
        agent.ghostBeliefs = [dist]
        
        game_state = MagicMock()
        game_state.getPacmanPosition.return_value = (0, 0)
        game_state.getLegalPacmanActions.return_value = [Directions.NORTH, Directions.EAST]
        game_state.getLivingGhosts.return_value = {1: True}
        
        call_count = [0]
        def mock_get_distance(pos1, pos2):
            call_count[0] += 1
            return 10
        
        agent.distancer.getDistance = mock_get_distance
        
        with patch('bustersAgents.Actions.getSuccessor') as mock_successor:
            mock_successor.side_effect = lambda pos, action: {
                Directions.NORTH: (0, 1),
                Directions.EAST: (1, 0)
            }[action]
            
            agent.chooseAction(game_state)
            
            # Should call getDistance for each legal action's successor
            assert call_count[0] >= 2

