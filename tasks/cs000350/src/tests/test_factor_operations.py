"""
Unit tests for factor operations (Q2, Q3)
"""
import pytest
import sys
import os

# Add tracking directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tracking'))

from bayesNet import Factor
from factorOperations import joinFactors, eliminate


class TestJoinFactors:
    """Tests for Q2: joinFactors"""
    
    def test_join_single_factor(self):
        """Test joining a single factor returns itself"""
        var_domains = {'A': [1, 2]}
        factor = Factor(['A'], [], var_domains)
        factor.setProbability({'A': 1}, 0.3)
        factor.setProbability({'A': 2}, 0.7)
        
        result = joinFactors([factor])
        
        assert result.unconditionedVariables() == factor.unconditionedVariables()
        assert result.getProbability({'A': 1}) == 0.3
        assert result.getProbability({'A': 2}) == 0.7
    
    def test_join_two_independent_factors(self):
        """Test joining two independent factors"""
        var_domains = {'A': [1, 2], 'B': [3, 4]}
        factor1 = Factor(['A'], [], var_domains)
        factor2 = Factor(['B'], [], var_domains)
        
        factor1.setProbability({'A': 1}, 0.4)
        factor1.setProbability({'A': 2}, 0.6)
        factor2.setProbability({'B': 3}, 0.3)
        factor2.setProbability({'B': 4}, 0.7)
        
        result = joinFactors([factor1, factor2])
        
        assert 'A' in result.unconditionedVariables()
        assert 'B' in result.unconditionedVariables()
        assert result.getProbability({'A': 1, 'B': 3}) == pytest.approx(0.4 * 0.3)
        assert result.getProbability({'A': 1, 'B': 4}) == pytest.approx(0.4 * 0.7)
        assert result.getProbability({'A': 2, 'B': 3}) == pytest.approx(0.6 * 0.3)
        assert result.getProbability({'A': 2, 'B': 4}) == pytest.approx(0.6 * 0.7)
    
    def test_join_with_conditioned_variables(self):
        """Test joining factors with conditioned variables"""
        var_domains = {'A': [1, 2], 'B': [3, 4], 'C': [5, 6]}
        factor1 = Factor(['A'], ['B'], var_domains)
        factor2 = Factor(['C'], ['B'], var_domains)
        
        factor1.setProbability({'A': 1, 'B': 3}, 0.2)
        factor1.setProbability({'A': 1, 'B': 4}, 0.3)
        factor1.setProbability({'A': 2, 'B': 3}, 0.4)
        factor1.setProbability({'A': 2, 'B': 4}, 0.1)
        factor2.setProbability({'C': 5, 'B': 3}, 0.6)
        factor2.setProbability({'C': 6, 'B': 3}, 0.4)
        factor2.setProbability({'C': 5, 'B': 4}, 0.7)
        factor2.setProbability({'C': 6, 'B': 4}, 0.3)
        
        result = joinFactors([factor1, factor2])
        
        assert 'A' in result.unconditionedVariables()
        assert 'C' in result.unconditionedVariables()
        assert 'B' in result.conditionedVariables()
        assert result.getProbability({'A': 1, 'B': 3, 'C': 5}) == pytest.approx(0.2 * 0.6)
    
    def test_join_empty_list_raises_error(self):
        """Test that joining empty list raises error"""
        with pytest.raises(ValueError):
            joinFactors([])


class TestEliminate:
    """Tests for Q3: eliminate"""
    
    def test_eliminate_single_unconditioned(self):
        """Test eliminating one unconditioned variable"""
        var_domains = {'A': [1, 2], 'B': [3, 4]}
        factor = Factor(['A', 'B'], [], var_domains)
        
        factor.setProbability({'A': 1, 'B': 3}, 0.1)
        factor.setProbability({'A': 1, 'B': 4}, 0.2)
        factor.setProbability({'A': 2, 'B': 3}, 0.3)
        factor.setProbability({'A': 2, 'B': 4}, 0.4)
        
        result = eliminate(factor, 'A')
        
        assert 'A' not in result.unconditionedVariables()
        assert 'B' in result.unconditionedVariables()
        assert result.getProbability({'B': 3}) == pytest.approx(0.1 + 0.3)
        assert result.getProbability({'B': 4}) == pytest.approx(0.2 + 0.4)
    
    def test_eliminate_with_conditioned_variables(self):
        """Test eliminating variable when conditioned variables exist"""
        var_domains = {'A': [1, 2], 'B': [3, 4], 'C': [5, 6]}
        factor = Factor(['A', 'B'], ['C'], var_domains)
        
        factor.setProbability({'A': 1, 'B': 3, 'C': 5}, 0.1)
        factor.setProbability({'A': 1, 'B': 4, 'C': 5}, 0.2)
        factor.setProbability({'A': 2, 'B': 3, 'C': 5}, 0.3)
        factor.setProbability({'A': 2, 'B': 4, 'C': 5}, 0.4)
        
        result = eliminate(factor, 'A')
        
        assert 'A' not in result.unconditionedVariables()
        assert 'B' in result.unconditionedVariables()
        assert 'C' in result.conditionedVariables()
        assert result.getProbability({'B': 3, 'C': 5}) == pytest.approx(0.1 + 0.3)
        assert result.getProbability({'B': 4, 'C': 5}) == pytest.approx(0.2 + 0.4)
    
    def test_eliminate_preserves_probability_sum(self):
        """Test that elimination preserves total probability"""
        var_domains = {'A': [1, 2], 'B': [3, 4]}
        factor = Factor(['A', 'B'], [], var_domains)
        
        factor.setProbability({'A': 1, 'B': 3}, 0.1)
        factor.setProbability({'A': 1, 'B': 4}, 0.2)
        factor.setProbability({'A': 2, 'B': 3}, 0.3)
        factor.setProbability({'A': 2, 'B': 4}, 0.4)
        
        result = eliminate(factor, 'A')
        
        total = sum(result.getProbability({'B': b}) for b in [3, 4])
        assert total == pytest.approx(1.0)

