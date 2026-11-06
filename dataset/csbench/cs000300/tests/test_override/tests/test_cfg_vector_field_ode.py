"""
Unit tests for CFGVectorFieldODE
"""
import pytest
import torch
from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab_three import CFGVectorFieldODE, ConditionalVectorField


class MockVectorField(ConditionalVectorField):
    """Mock vector field that returns predictable outputs"""
    def __init__(self, guided_value=1.0, unguided_value=0.0):
        super().__init__()
        self.guided_value = guided_value
        self.unguided_value = unguided_value
    
    def forward(self, x, t, y):
        # Return guided_value for non-null labels, unguided_value for null label (10)
        result = torch.ones_like(x) * self.unguided_value
        mask = (y != 10)
        result[mask] = self.guided_value
        return result


class TestCFGVectorFieldODE:
    """Test cases for CFGVectorFieldODE"""
    
    def test_initialization(self):
        """Test CFGVectorFieldODE initialization"""
        net = MockVectorField()
        ode = CFGVectorFieldODE(net, guidance_scale=2.0)
        
        assert ode.net == net
        assert ode.guidance_scale == 2.0
    
    def test_drift_coefficient_with_guidance_scale_one(self):
        """Test drift coefficient with guidance_scale=1.0"""
        net = MockVectorField(guided_value=2.0, unguided_value=1.0)
        ode = CFGVectorFieldODE(net, guidance_scale=1.0)
        
        x = torch.randn(3, 1, 32, 32)
        t = torch.rand(3, 1, 1, 1)
        y = torch.tensor([0, 1, 2])
        
        drift = ode.drift_coefficient(x, t, y)
        
        assert drift.shape == (3, 1, 32, 32)
        # With w=1.0, should get guided vector field
        assert torch.allclose(drift, torch.ones_like(drift) * 2.0)
    
    def test_drift_coefficient_with_guidance_scale_zero(self):
        """Test drift coefficient with guidance_scale=0.0"""
        net = MockVectorField(guided_value=2.0, unguided_value=1.0)
        ode = CFGVectorFieldODE(net, guidance_scale=0.0)
        
        x = torch.randn(3, 1, 32, 32)
        t = torch.rand(3, 1, 1, 1)
        y = torch.tensor([0, 1, 2])
        
        drift = ode.drift_coefficient(x, t, y)
        
        assert drift.shape == (3, 1, 32, 32)
        # With w=0.0, should get unguided vector field
        assert torch.allclose(drift, torch.ones_like(drift) * 1.0)
    
    def test_drift_coefficient_with_guidance_scale_greater_than_one(self):
        """Test drift coefficient with guidance_scale > 1.0"""
        net = MockVectorField(guided_value=2.0, unguided_value=1.0)
        ode = CFGVectorFieldODE(net, guidance_scale=3.0)
        
        x = torch.randn(3, 1, 32, 32)
        t = torch.rand(3, 1, 1, 1)
        y = torch.tensor([0, 1, 2])
        
        drift = ode.drift_coefficient(x, t, y)
        
        assert drift.shape == (3, 1, 32, 32)
        # With w=3.0: (1-3)*1.0 + 3*2.0 = -2.0 + 6.0 = 4.0
        expected = torch.ones_like(drift) * 4.0
        assert torch.allclose(drift, expected)
    
    def test_drift_coefficient_uses_null_label(self):
        """Test that drift coefficient uses null label (10) for unguided vector field"""
        net = MockVectorField(guided_value=2.0, unguided_value=1.0)
        ode = CFGVectorFieldODE(net, guidance_scale=2.0)
        
        x = torch.randn(3, 1, 32, 32)
        t = torch.rand(3, 1, 1, 1)
        y = torch.tensor([0, 1, 2])
        
        # Track calls to net.forward
        original_forward = net.forward
        call_labels = []
        def tracked_forward(x, t, y):
            call_labels.append(y.clone())
            return original_forward(x, t, y)
        
        net.forward = tracked_forward
        
        ode.drift_coefficient(x, t, y)
        
        # Should call with original labels and null labels
        assert len(call_labels) == 2
        assert torch.all(call_labels[1] == 10)  # Second call should use null label
    
    def test_drift_coefficient_output_shape(self):
        """Test that drift coefficient returns correct shape"""
        net = MockVectorField()
        ode = CFGVectorFieldODE(net, guidance_scale=2.0)
        
        batch_sizes = [1, 4, 8, 16]
        for bs in batch_sizes:
            x = torch.randn(bs, 1, 32, 32)
            t = torch.rand(bs, 1, 1, 1)
            y = torch.randint(0, 10, (bs,))
            
            drift = ode.drift_coefficient(x, t, y)
            
            assert drift.shape == (bs, 1, 32, 32)
    
    def test_drift_coefficient_with_large_guidance_scale(self):
        """Test drift coefficient with very large guidance scale"""
        net = MockVectorField(guided_value=2.0, unguided_value=1.0)
        ode = CFGVectorFieldODE(net, guidance_scale=10.0)
        
        x = torch.randn(2, 1, 32, 32)
        t = torch.rand(2, 1, 1, 1)
        y = torch.tensor([0, 1])
        
        drift = ode.drift_coefficient(x, t, y)
        
        assert drift.shape == (2, 1, 32, 32)
        # With w=10.0: (1-10)*1.0 + 10*2.0 = -9.0 + 20.0 = 11.0
        expected = torch.ones_like(drift) * 11.0
        assert torch.allclose(drift, expected)

