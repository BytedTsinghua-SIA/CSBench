"""
Unit tests for variable elimination (Q4)
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add tracking directory to path
tracking_path = os.path.join(os.path.dirname(__file__), '..', 'tracking')
if tracking_path not in sys.path:
    sys.path.insert(0, tracking_path)

from inference import inferenceByVariableElimination
from bayesNet import BayesNet, Factor


class TestVariableElimination:
    """Tests for Q4: inferenceByVariableElimination"""
    
    def test_simple_elimination(self):
        """Test simple variable elimination"""
        variables = ['A', 'B']
        in_edges = {'A': set(), 'B': {'A'}}
        out_edges = {'A': {'B'}, 'B': set()}
        var_domains = {'A': [1, 2], 'B': [3, 4]}
        
        net = BayesNet(variables, in_edges, out_edges, var_domains)
        
        # Create CPTs
        cpt_a = Factor(['A'], [], var_domains)
        cpt_a.setProbability({'A': 1}, 0.6)
        cpt_a.setProbability({'A': 2}, 0.4)
        net.setCPT('A', cpt_a)
        
        cpt_b = Factor(['B'], ['A'], var_domains)
        cpt_b.setProbability({'B': 3, 'A': 1}, 0.7)
        cpt_b.setProbability({'B': 4, 'A': 1}, 0.3)
        cpt_b.setProbability({'B': 3, 'A': 2}, 0.2)
        cpt_b.setProbability({'B': 4, 'A': 2}, 0.8)
        net.setCPT('B', cpt_b)
        
        result = inferenceByVariableElimination(net, ['B'], {}, ['A'])
        
        assert 'B' in result.unconditionedVariables()
        assert 'A' not in result.unconditionedVariables()
        total = sum(result.getProbability({'B': b}) for b in [3, 4])
        assert total == pytest.approx(1.0)
    
    def test_elimination_with_evidence(self):
        """Test variable elimination with evidence"""
        variables = ['A', 'B', 'C']
        in_edges = {'A': set(), 'B': {'A'}, 'C': {'B'}}
        out_edges = {'A': {'B'}, 'B': {'C'}, 'C': set()}
        var_domains = {'A': [1, 2], 'B': [3, 4], 'C': [5, 6]}
        
        net = BayesNet(variables, in_edges, out_edges, var_domains)
        
        cpt_a = Factor(['A'], [], var_domains)
        cpt_a.setProbability({'A': 1}, 0.5)
        cpt_a.setProbability({'A': 2}, 0.5)
        net.setCPT('A', cpt_a)
        
        cpt_b = Factor(['B'], ['A'], var_domains)
        for a in [1, 2]:
            for b in [3, 4]:
                cpt_b.setProbability({'B': b, 'A': a}, 0.5)
        net.setCPT('B', cpt_b)
        
        cpt_c = Factor(['C'], ['B'], var_domains)
        for b in [3, 4]:
            for c in [5, 6]:
                cpt_c.setProbability({'C': c, 'B': b}, 0.5)
        net.setCPT('C', cpt_c)
        
        evidence = {'C': 5}
        result = inferenceByVariableElimination(net, ['A'], evidence, ['B'])
        
        assert 'A' in result.unconditionedVariables()
        assert 'C' in result.conditionedVariables()
        total = sum(result.getProbability({'A': a, 'C': 5}) for a in [1, 2])
        assert total == pytest.approx(1.0)
    
    def test_elimination_returns_normalized_result(self):
        """Test that elimination result is normalized"""
        variables = ['A', 'B']
        in_edges = {'A': set(), 'B': {'A'}}
        out_edges = {'A': {'B'}, 'B': set()}
        var_domains = {'A': [1, 2], 'B': [3, 4]}
        
        net = BayesNet(variables, in_edges, out_edges, var_domains)
        
        cpt_a = Factor(['A'], [], var_domains)
        cpt_a.setProbability({'A': 1}, 0.3)
        cpt_a.setProbability({'A': 2}, 0.7)
        net.setCPT('A', cpt_a)
        
        cpt_b = Factor(['B'], ['A'], var_domains)
        cpt_b.setProbability({'B': 3, 'A': 1}, 1.0)
        cpt_b.setProbability({'B': 4, 'A': 1}, 0.0)
        cpt_b.setProbability({'B': 3, 'A': 2}, 0.0)
        cpt_b.setProbability({'B': 4, 'A': 2}, 1.0)
        net.setCPT('B', cpt_b)
        
        result = inferenceByVariableElimination(net, ['B'], {}, ['A'])
        
        total = sum(result.getProbability({'B': b}) for b in [3, 4])
        assert total == pytest.approx(1.0)

