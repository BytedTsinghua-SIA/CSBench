"""
Unit tests for fully_connected_networks.py
"""

import torch
import unittest
import numpy as np
from fully_connected_networks import *
from a3_helper import softmax_loss


class TestFullyConnectedNetworks(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.dtype = torch.float64
        self.device = 'cpu'
        
    def test_linear_forward(self):
        """Test Linear.forward implementation"""
        print("Testing Linear.forward...")
        
        # Test parameters
        N, D, M = 4, 5, 6
        x = torch.randn(N, D, dtype=self.dtype, device=self.device)
        w = torch.randn(D, M, dtype=self.dtype, device=self.device)
        b = torch.randn(M, dtype=self.dtype, device=self.device)
        
        # Forward pass
        out, _ = Linear.forward(x, w, b)
        
        # Expected output
        expected_out = torch.mm(x, w) + b
        
        # Check correctness
        self.assertTrue(torch.allclose(out, expected_out, rtol=1e-5, atol=1e-6),
                       "Linear forward pass failed")
        print("Linear.forward test passed!")
        
    def test_linear_backward(self):
        """Test Linear.backward implementation"""
        print("Testing Linear.backward...")
        
        # Test parameters
        N, D, M = 4, 5, 6
        x = torch.randn(N, D, dtype=self.dtype, device=self.device)
        w = torch.randn(D, M, dtype=self.dtype, device=self.device)
        b = torch.randn(M, dtype=self.dtype, device=self.device)
        
        # Forward pass
        out, cache = Linear.forward(x, w, b)
        
        # Backward pass
        dout = torch.randn_like(out)
        dx, dw, db = Linear.backward(dout, cache)
        
        # Numerical gradient check
        def f(x):
            out, _ = Linear.forward(x, w, b)
            return out
        
        def numerical_gradient_x(x, dout, h=1e-5):
            grad = torch.zeros_like(x)
            for i in range(x.numel()):
                x_flat = x.flatten()
                x_plus = x_flat.clone()
                x_minus = x_flat.clone()
                x_plus[i] += h
                x_minus[i] -= h
                
                x_plus_reshaped = x_plus.reshape(x.shape)
                x_minus_reshaped = x_minus.reshape(x.shape)
                
                f_plus = torch.sum(f(x_plus_reshaped) * dout)
                f_minus = torch.sum(f(x_minus_reshaped) * dout)
                grad_flat = grad.flatten()
                grad_flat[i] = (f_plus - f_minus) / (2 * h)
                grad = grad_flat.reshape(x.shape)
            return grad
        
        # Check gradient w.r.t x
        dx_num = numerical_gradient_x(x, dout)
        self.assertTrue(torch.allclose(dx, dx_num, rtol=1e-4, atol=1e-5),
                       "Linear backward pass (dx) failed")
        print("Linear.backward test passed!")
        
    def test_relu_forward(self):
        """Test ReLU.forward implementation"""
        print("Testing ReLU.forward...")
        
        x = torch.randn(10, 10, dtype=self.dtype, device=self.device)
        out, _ = ReLU.forward(x)
        
        expected_out = torch.clamp(x, min=0)
        
        self.assertTrue(torch.allclose(out, expected_out, rtol=1e-5, atol=1e-6),
                       "ReLU forward pass failed")
        print("ReLU.forward test passed!")
        
    def test_relu_backward(self):
        """Test ReLU.backward implementation"""
        print("Testing ReLU.backward...")
        
        x = torch.randn(10, 10, dtype=self.dtype, device=self.device)
        out, cache = ReLU.forward(x)
        
        dout = torch.randn_like(out)
        dx = ReLU.backward(dout, cache)
        
        expected_dx = dout * (x > 0).float()
        
        self.assertTrue(torch.allclose(dx, expected_dx, rtol=1e-5, atol=1e-6),
                       "ReLU backward pass failed")
        print("ReLU.backward test passed!")
        
    def test_two_layer_net_forward(self):
        """Test TwoLayerNet forward pass"""
        print("Testing TwoLayerNet forward pass...")
        
        N, D, H, C = 4, 5, 10, 3
        model = TwoLayerNet(input_dim=D, hidden_dim=H, num_classes=C,
                           weight_scale=1e-2, dtype=self.dtype, device=self.device)
        
        X = torch.randn(N, D, dtype=self.dtype, device=self.device)
        scores = model.loss(X)
        
        # Check output shape
        self.assertEqual(scores.shape, (N, C), "TwoLayerNet output shape incorrect")
        
        # Check that scores are computed correctly
        W1, b1 = model.params['W1'], model.params['b1']
        W2, b2 = model.params['W2'], model.params['b2']
        
        h1 = torch.clamp(torch.mm(X, W1) + b1, min=0)  # ReLU
        expected_scores = torch.mm(h1, W2) + b2
        
        self.assertTrue(torch.allclose(scores, expected_scores, rtol=1e-5, atol=1e-6),
                       "TwoLayerNet forward pass failed")
        print("TwoLayerNet forward test passed!")
        
    def test_two_layer_net_backward(self):
        """Test TwoLayerNet backward pass"""
        print("Testing TwoLayerNet backward pass...")
        
        N, D, H, C = 4, 5, 10, 3
        model = TwoLayerNet(input_dim=D, hidden_dim=H, num_classes=C,
                           weight_scale=1e-2, dtype=self.dtype, device=self.device)
        
        X = torch.randn(N, D, dtype=self.dtype, device=self.device)
        y = torch.randint(0, C, (N,), dtype=torch.long, device=self.device)
        
        loss, grads = model.loss(X, y)
        
        # Check that gradients are computed
        self.assertIn('W1', grads)
        self.assertIn('b1', grads)
        self.assertIn('W2', grads)
        self.assertIn('b2', grads)
        
        # Check gradient shapes
        self.assertEqual(grads['W1'].shape, model.params['W1'].shape)
        self.assertEqual(grads['b1'].shape, model.params['b1'].shape)
        self.assertEqual(grads['W2'].shape, model.params['W2'].shape)
        self.assertEqual(grads['b2'].shape, model.params['b2'].shape)
        
        print("TwoLayerNet backward test passed!")
        
    def test_fully_connected_net(self):
        """Test FullyConnectedNet"""
        print("Testing FullyConnectedNet...")
        
        N, D, H1, H2, C = 4, 5, 10, 8, 3
        hidden_dims = [H1, H2]
        model = FullyConnectedNet(hidden_dims, input_dim=D, num_classes=C,
                                 weight_scale=1e-2, dtype=self.dtype, device=self.device)
        
        X = torch.randn(N, D, dtype=self.dtype, device=self.device)
        y = torch.randint(0, C, (N,), dtype=torch.long, device=self.device)
        
        loss, grads = model.loss(X, y)
        
        # Check that loss is a scalar
        self.assertEqual(loss.shape, (), "Loss should be a scalar")
        
        # Check that all gradients are computed
        for i in range(1, len(hidden_dims) + 2):
            self.assertIn('W%d' % i, grads)
            self.assertIn('b%d' % i, grads)
        
        print("FullyConnectedNet test passed!")
        
    def test_sgd_momentum(self):
        """Test SGD with momentum"""
        print("Testing SGD with momentum...")
        
        w = torch.randn(10, 10, dtype=self.dtype, device=self.device)
        dw = torch.randn(10, 10, dtype=self.dtype, device=self.device)
        
        config = {'learning_rate': 1e-2, 'momentum': 0.9}
        
        next_w, next_config = sgd_momentum(w, dw, config)
        
        # Check that velocity is initialized
        self.assertIn('velocity', next_config)
        
        # Check that weight was updated
        self.assertFalse(torch.equal(w, next_w), "Weights should be updated")
        
        print("SGD momentum test passed!")
        
    def test_adam(self):
        """Test Adam optimizer"""
        print("Testing Adam optimizer...")
        
        w = torch.randn(10, 10, dtype=self.dtype, device=self.device)
        dw = torch.randn(10, 10, dtype=self.dtype, device=self.device)
        
        config = {'learning_rate': 1e-3}
        
        next_w, next_config = adam(w, dw, config)
        
        # Check that m, v, and t are initialized
        self.assertIn('m', next_config)
        self.assertIn('v', next_config)
        self.assertIn('t', next_config)
        self.assertEqual(next_config['t'], 1)
        
        # Check that weight was updated
        self.assertFalse(torch.equal(w, next_w), "Weights should be updated")
        
        print("Adam test passed!")
        
    def test_dropout(self):
        """Test Dropout implementation"""
        print("Testing Dropout...")
        
        x = torch.randn(10, 10, dtype=self.dtype, device=self.device)
        
        # Test training mode
        dropout_param = {'p': 0.5, 'mode': 'train'}
        out_train, cache_train = Dropout.forward(x, dropout_param)
        
        # Check that some elements are zeroed out
        self.assertTrue(torch.sum(out_train == 0) > 0, "Some elements should be zeroed in training mode")
        
        # Test test mode
        dropout_param = {'p': 0.5, 'mode': 'test'}
        out_test, cache_test = Dropout.forward(x, dropout_param)
        
        # Check that no elements are zeroed in test mode
        self.assertTrue(torch.allclose(out_test, x), "Test mode should not modify input")
        
        # Test backward pass
        dout = torch.randn_like(out_train)
        dx = Dropout.backward(dout, cache_train)
        
        # Check that gradient is scaled correctly
        self.assertEqual(dx.shape, x.shape, "Gradient shape should match input shape")
        
        print("Dropout test passed!")


if __name__ == '__main__':
    unittest.main()