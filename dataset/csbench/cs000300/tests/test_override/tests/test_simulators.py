"""
Unit tests for Simulator classes
"""
import pytest
import torch
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab_three import EulerSimulator, EulerMaruyamaSimulator, ODE, SDE


class MockODE(ODE):
    """Mock ODE for testing"""
    def __init__(self, drift_value=1.0):
        self.drift_value = drift_value
    
    def drift_coefficient(self, xt, t, **kwargs):
        return torch.ones_like(xt) * self.drift_value


class MockSDE(SDE):
    """Mock SDE for testing"""
    def __init__(self, drift_value=1.0, diffusion_value=0.1):
        self.drift_value = drift_value
        self.diffusion_value = diffusion_value
    
    def drift_coefficient(self, xt, t, **kwargs):
        return torch.ones_like(xt) * self.drift_value
    
    def diffusion_coefficient(self, xt, t, **kwargs):
        return torch.ones_like(xt) * self.diffusion_value


class TestEulerSimulator:
    """Test cases for EulerSimulator"""
    
    def test_initialization(self):
        """Test EulerSimulator initialization"""
        ode = MockODE()
        simulator = EulerSimulator(ode)
        
        assert simulator.ode == ode
    
    def test_step_output_shape(self):
        """Test step output shape"""
        ode = MockODE()
        simulator = EulerSimulator(ode)
        
        xt = torch.randn(4, 1, 32, 32)
        t = torch.rand(4, 1, 1, 1)
        h = torch.ones(4, 1, 1, 1) * 0.1
        
        nxt = simulator.step(xt, t, h)
        
        assert nxt.shape == xt.shape
    
    def test_step_implements_euler_method(self):
        """Test that step implements Euler method: x_{t+h} = x_t + f(x_t, t) * h"""
        ode = MockODE(drift_value=2.0)
        simulator = EulerSimulator(ode)
        
        xt = torch.ones(2, 1, 32, 32)
        t = torch.rand(2, 1, 1, 1)
        h = torch.ones(2, 1, 1, 1) * 0.5
        
        nxt = simulator.step(xt, t, h)
        
        # Expected: 1.0 + 2.0 * 0.5 = 2.0
        expected = torch.ones_like(xt) * 2.0
        assert torch.allclose(nxt, expected)
    
    def test_step_with_different_step_sizes(self):
        """Test step with different step sizes"""
        ode = MockODE(drift_value=1.0)
        simulator = EulerSimulator(ode)
        
        xt = torch.zeros(2, 1, 32, 32)
        t = torch.rand(2, 1, 1, 1)
        
        # Test a couple of step sizes
        for h_val in [0.1, 0.5]:
            h = torch.ones(2, 1, 1, 1) * h_val
            nxt = simulator.step(xt, t, h)
            expected = torch.ones_like(xt) * h_val
            assert torch.allclose(nxt, expected)


class TestEulerMaruyamaSimulator:
    """Test cases for EulerMaruyamaSimulator"""
    
    def test_initialization(self):
        """Test EulerMaruyamaSimulator initialization"""
        sde = MockSDE()
        simulator = EulerMaruyamaSimulator(sde)
        
        assert simulator.sde == sde
    
    def test_step_output_shape(self):
        """Test step output shape"""
        sde = MockSDE()
        simulator = EulerMaruyamaSimulator(sde)
        
        xt = torch.randn(4, 1, 32, 32)
        t = torch.rand(4, 1, 1, 1)
        h = torch.ones(4, 1, 1, 1) * 0.1
        
        nxt = simulator.step(xt, t, h)
        
        assert nxt.shape == xt.shape
    
    def test_step_includes_noise(self):
        """Test that step includes stochastic noise"""
        sde = MockSDE(drift_value=0.0, diffusion_value=1.0)
        simulator = EulerMaruyamaSimulator(sde)
        
        xt = torch.zeros(100, 1, 32, 32)
        t = torch.rand(100, 1, 1, 1)
        h = torch.ones(100, 1, 1, 1) * 0.1
        
        # Run multiple steps and check variance
        results = []
        for _ in range(10):
            nxt = simulator.step(xt, t, h)
            results.append(nxt)
        
        # Results should have non-zero variance due to noise
        all_results = torch.stack(results)
        variance = all_results.var()
        assert variance > 0.01  # Should have some variance from noise
    
    def test_step_deterministic_part(self):
        """Test deterministic part of Euler-Maruyama"""
        sde = MockSDE(drift_value=2.0, diffusion_value=0.0)
        simulator = EulerMaruyamaSimulator(sde)
        
        xt = torch.ones(2, 1, 32, 32)
        t = torch.rand(2, 1, 1, 1)
        h = torch.ones(2, 1, 1, 1) * 0.5
        
        # Set random seed for reproducibility
        torch.manual_seed(42)
        nxt = simulator.step(xt, t, h)
        
        # With zero diffusion, should behave like Euler
        expected = torch.ones_like(xt) * 2.0
        assert torch.allclose(nxt, expected, atol=0.1)
    
    def test_simulate_method(self):
        """Test simulate method runs multiple steps"""
        ode = MockODE(drift_value=1.0)
        simulator = EulerSimulator(ode)
        
        x0 = torch.zeros(2, 1, 32, 32)
        ts = torch.linspace(0, 1, 5).view(1, -1, 1, 1, 1).expand(2, -1, 1, 1, 1)
        
        x_final = simulator.simulate(x0, ts)
        
        assert x_final.shape == (2, 1, 32, 32)
        # After 4 steps with h=0.25 each, should be approximately 1.0
        assert torch.allclose(x_final, torch.ones_like(x_final), atol=0.1)
    
    def test_simulate_with_trajectory_method(self):
        """Test simulate_with_trajectory method returns full trajectory"""
        ode = MockODE(drift_value=1.0)
        simulator = EulerSimulator(ode)
        
        x0 = torch.zeros(2, 1, 32, 32)
        ts = torch.linspace(0, 1, 5).view(1, -1, 1, 1, 1).expand(2, -1, 1, 1, 1)
        
        trajectory = simulator.simulate_with_trajectory(x0, ts)
        
        assert trajectory.shape == (2, 5, 1, 32, 32)
        # First element should be initial state
        assert torch.allclose(trajectory[:, 0], x0)
        # Last element should be final state
        assert trajectory.shape[1] == 5

