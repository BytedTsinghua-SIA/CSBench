"""
Unit tests for basic inference functions (Q1, Q4, Q5a, Q5b)
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add tracking directory to path
tracking_path = os.path.join(os.path.dirname(__file__), '..', 'tracking')
if tracking_path not in sys.path:
    sys.path.insert(0, tracking_path)

from inference import constructBayesNet, DiscreteDistribution, InferenceModule
from bayesNet import Factor
import busters


class TestConstructBayesNet:
    """Tests for Q1: constructBayesNet"""
    
    def test_creates_correct_variables(self):
        """Test that all required variables are created"""
        game_state = MagicMock()
        walls = MagicMock()
        walls.width = 5
        walls.height = 5
        game_state.getWalls.return_value = walls
        
        net = constructBayesNet(game_state)
        
        variables = net.variablesSet()
        assert "Pacman" in variables
        assert "Ghost0" in variables
        assert "Ghost1" in variables
        assert "Observation0" in variables
        assert "Observation1" in variables
    
    def test_creates_correct_edges(self):
        """Test that correct edges are created"""
        game_state = MagicMock()
        walls = MagicMock()
        walls.width = 3
        walls.height = 3
        game_state.getWalls.return_value = walls
        
        net = constructBayesNet(game_state)
        edges = net.outEdges()
        
        assert "Pacman" in edges
        assert "Observation0" in edges["Pacman"]
        assert "Observation1" in edges["Pacman"]
        assert "Ghost0" in edges
        assert "Observation0" in edges["Ghost0"]
        assert "Ghost1" in edges
        assert "Observation1" in edges["Ghost1"]
    
    def test_variable_domains_are_set(self):
        """Test that variable domains are properly set"""
        game_state = MagicMock()
        walls = MagicMock()
        walls.width = 4
        walls.height = 4
        game_state.getWalls.return_value = walls
        
        net = constructBayesNet(game_state)
        domains = net.variableDomainsDict()
        
        assert "Pacman" in domains
        assert len(domains["Pacman"]) == 16  # 4 * 4 positions
        assert "Observation0" in domains
        assert None in domains["Observation0"] or 0 in domains["Observation0"]


class TestDiscreteDistribution:
    """Tests for Q5a: DiscreteDistribution"""
    
    def test_normalize_basic(self):
        """Test basic normalization"""
        dist = DiscreteDistribution()
        dist['a'] = 1
        dist['b'] = 2
        dist['c'] = 2
        
        dist.normalize()
        
        assert dist['a'] == pytest.approx(0.2)
        assert dist['b'] == pytest.approx(0.4)
        assert dist['c'] == pytest.approx(0.4)
        assert sum(dist.values()) == pytest.approx(1.0)
    
    def test_normalize_empty_distribution(self):
        """Test normalizing empty distribution does nothing"""
        dist = DiscreteDistribution()
        dist.normalize()
        assert len(dist) == 0
    
    def test_normalize_zero_total(self):
        """Test normalizing distribution with zero total does nothing"""
        dist = DiscreteDistribution()
        dist['a'] = 0
        dist['b'] = 0
        dist.normalize()
        assert dist['a'] == 0
        assert dist['b'] == 0
    
    def test_sample_basic(self):
        """Test basic sampling"""
        dist = DiscreteDistribution()
        dist['a'] = 1
        dist['b'] = 2
        dist['c'] = 2
        dist.normalize()
        
        samples = [dist.sample() for _ in range(1000)]
        
        assert 'a' in samples
        assert 'b' in samples
        assert 'c' in samples
        # Check approximate proportions
        a_count = samples.count('a') / 1000.0
        assert 0.15 < a_count < 0.25
    
    def test_sample_zero_probability(self):
        """Test sampling from distribution with zero probabilities"""
        dist = DiscreteDistribution()
        dist['a'] = 1
        dist['b'] = 0
        dist.normalize()
        
        samples = [dist.sample() for _ in range(100)]
        assert 'b' not in samples or samples.count('b') == 0


class TestGetObservationProb:
    """Tests for Q5b: getObservationProb"""
    
    def test_observation_prob_jail_position(self):
        """Test observation probability when ghost is in jail"""
        module = InferenceModule(MagicMock())
        module.getJailPosition = lambda: (1, 1)
        
        prob = module.getObservationProb(None, (0, 0), (1, 1), (1, 1))
        assert prob == 1.0
        
        prob = module.getObservationProb(5, (0, 0), (1, 1), (1, 1))
        assert prob == 0.0
    
    def test_observation_prob_none_observation(self):
        """Test observation probability when observation is None"""
        module = InferenceModule(MagicMock())
        module.getJailPosition = lambda: (10, 10)
        
        prob = module.getObservationProb(None, (0, 0), (3, 3), (10, 10))
        assert prob == 0.0
    
    @patch('inference.busters.getObservationProbability')
    def test_observation_prob_calls_busters_function(self, mock_func):
        """Test that getObservationProb calls busters function correctly"""
        mock_func.return_value = 0.5
        module = InferenceModule(MagicMock())
        module.getJailPosition = lambda: (10, 10)
        
        prob = module.getObservationProb(5, (0, 0), (3, 3), (10, 10))
        
        assert mock_func.called
        assert prob == 0.5

