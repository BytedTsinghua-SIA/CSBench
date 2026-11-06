"""
Unit tests for convolutional_networks.py
"""

import torch
import unittest
import numpy as np
from convolutional_networks import *
from a3_helper import softmax_loss


class TestConvolutionalNetworks(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.dtype = torch.float64
        self.device = 'cpu'
        
    def test_conv_forward(self):
        """Test Conv.forward implementation"""
        print("Testing Conv.forward...")
        
        # Test parameters
        N, C, H, W = 2, 3, 5, 5
        F, HH, WW = 4, 3, 3
        stride, pad = 1, 1
        
        x = torch.randn(N, C, H, W, dtype=self.dtype, device=self.device)
        w = torch.randn(F, C, HH, WW, dtype=self.dtype, device=self.device)
        b = torch.randn(F, dtype=self.dtype, device=self.device)
        conv_param = {'stride': stride, 'pad': pad}
        
        # Forward pass
        out, cache = Conv.forward(x, w, b, conv_param)
        
        # Expected output dimensions
        H_out = 1 + (H + 2 * pad - HH) // stride
        W_out = 1 + (W + 2 * pad - WW) // stride
        
        # Check output shape
        self.assertEqual(out.shape, (N, F, H_out, W_out), "Conv output shape incorrect")
        
        # Check that output is computed correctly for a few positions
        x_padded = torch.nn.functional.pad(x, (pad, pad, pad, pad))
        for n in range(N):
            for f in range(F):
                for i in range(H_out):
                    for j in range(W_out):
                        h_start = i * stride
                        h_end = h_start + HH
                        w_start = j * stride
                        w_end = w_start + WW
                        
                        x_slice = x_padded[n, :, h_start:h_end, w_start:w_end]
                        expected_val = torch.sum(x_slice * w[f]) + b[f]
                        
                        self.assertTrue(torch.allclose(out[n, f, i, j], expected_val, rtol=1e-5, atol=1e-6),
                                       f"Conv forward pass failed at position ({n}, {f}, {i}, {j})")
        
        print("Conv.forward test passed!")
        
    def test_conv_backward(self):
        """Test Conv.backward implementation"""
        print("Testing Conv.backward...")
        
        # Test parameters
        N, C, H, W = 2, 3, 5, 5
        F, HH, WW = 4, 3, 3
        stride, pad = 1, 1
        
        x = torch.randn(N, C, H, W, dtype=self.dtype, device=self.device)
        w = torch.randn(F, C, HH, WW, dtype=self.dtype, device=self.device)
        b = torch.randn(F, dtype=self.dtype, device=self.device)
        conv_param = {'stride': stride, 'pad': pad}
        
        # Forward pass
        out, cache = Conv.forward(x, w, b, conv_param)
        
        # Backward pass
        dout = torch.randn_like(out)
        dx, dw, db = Conv.backward(dout, cache)
        
        # Check gradient shapes
        self.assertEqual(dx.shape, x.shape, "dx shape incorrect")
        self.assertEqual(dw.shape, w.shape, "dw shape incorrect")
        self.assertEqual(db.shape, b.shape, "db shape incorrect")
        
        print("Conv.backward test passed!")
        
    def test_maxpool_forward(self):
        """Test MaxPool.forward implementation"""
        print("Testing MaxPool.forward...")
        
        # Test parameters
        N, C, H, W = 2, 3, 6, 6
        pool_height, pool_width = 2, 2
        stride = 2
        
        x = torch.randn(N, C, H, W, dtype=self.dtype, device=self.device)
        pool_param = {'pool_height': pool_height, 'pool_width': pool_width, 'stride': stride}
        
        # Forward pass
        out, cache = MaxPool.forward(x, pool_param)
        
        # Expected output dimensions
        H_out = 1 + (H - pool_height) // stride
        W_out = 1 + (W - pool_width) // stride
        
        # Check output shape
        self.assertEqual(out.shape, (N, C, H_out, W_out), "MaxPool output shape incorrect")
        
        # Check that max pooling is computed correctly
        for n in range(N):
            for c in range(C):
                for i in range(H_out):
                    for j in range(W_out):
                        h_start = i * stride
                        h_end = h_start + pool_height
                        w_start = j * stride
                        w_end = w_start + pool_width
                        
                        x_pool = x[n, c, h_start:h_end, w_start:w_end]
                        expected_val = torch.max(x_pool)
                        
                        self.assertTrue(torch.allclose(out[n, c, i, j], expected_val, rtol=1e-5, atol=1e-6),
                                       f"MaxPool forward pass failed at position ({n}, {c}, {i}, {j})")
        
        print("MaxPool.forward test passed!")
        
    def test_maxpool_backward(self):
        """Test MaxPool.backward implementation"""
        print("Testing MaxPool.backward...")
        
        # Test parameters
        N, C, H, W = 2, 3, 6, 6
        pool_height, pool_width = 2, 2
        stride = 2
        
        x = torch.randn(N, C, H, W, dtype=self.dtype, device=self.device)
        pool_param = {'pool_height': pool_height, 'pool_width': pool_width, 'stride': stride}
        
        # Forward pass
        out, cache = MaxPool.forward(x, pool_param)
        
        # Backward pass
        dout = torch.randn_like(out)
        dx = MaxPool.backward(dout, cache)
        
        # Check gradient shape
        self.assertEqual(dx.shape, x.shape, "dx shape incorrect")
        
        print("MaxPool.backward test passed!")
        
    def test_three_layer_convnet_forward(self):
        """Test ThreeLayerConvNet forward pass"""
        print("Testing ThreeLayerConvNet forward pass...")
        
        # Test parameters
        N, C, H, W = 2, 3, 8, 8
        num_filters = 4
        filter_size = 3
        hidden_dim = 10
        num_classes = 5
        
        model = ThreeLayerConvNet(input_dims=(C, H, W), num_filters=num_filters,
                                 filter_size=filter_size, hidden_dim=hidden_dim,
                                 num_classes=num_classes, dtype=self.dtype, device=self.device)
        
        X = torch.randn(N, C, H, W, dtype=self.dtype, device=self.device)
        scores = model.loss(X)
        
        # Check output shape
        self.assertEqual(scores.shape, (N, num_classes), "ThreeLayerConvNet output shape incorrect")
        
        print("ThreeLayerConvNet forward test passed!")
        
    def test_three_layer_convnet_backward(self):
        """Test ThreeLayerConvNet backward pass"""
        print("Testing ThreeLayerConvNet backward pass...")
        
        # Test parameters
        N, C, H, W = 2, 3, 8, 8
        num_filters = 4
        filter_size = 3
        hidden_dim = 10
        num_classes = 5
        
        model = ThreeLayerConvNet(input_dims=(C, H, W), num_filters=num_filters,
                                 filter_size=filter_size, hidden_dim=hidden_dim,
                                 num_classes=num_classes, dtype=self.dtype, device=self.device)
        
        X = torch.randn(N, C, H, W, dtype=self.dtype, device=self.device)
        y = torch.randint(0, num_classes, (N,), dtype=torch.long, device=self.device)
        
        loss, grads = model.loss(X, y)
        
        # Check that gradients are computed
        self.assertIn('W1', grads)
        self.assertIn('b1', grads)
        self.assertIn('W2', grads)
        self.assertIn('b2', grads)
        self.assertIn('W3', grads)
        self.assertIn('b3', grads)
        
        # Check gradient shapes
        self.assertEqual(grads['W1'].shape, model.params['W1'].shape)
        self.assertEqual(grads['b1'].shape, model.params['b1'].shape)
        self.assertEqual(grads['W2'].shape, model.params['W2'].shape)
        self.assertEqual(grads['b2'].shape, model.params['b2'].shape)
        self.assertEqual(grads['W3'].shape, model.params['W3'].shape)
        self.assertEqual(grads['b3'].shape, model.params['b3'].shape)
        
        print("ThreeLayerConvNet backward test passed!")
        
    def test_deep_convnet(self):
        """Test DeepConvNet"""
        print("Testing DeepConvNet...")
        
        # Test parameters
        N, C, H, W = 2, 3, 8, 8
        num_filters = [4, 8]
        max_pools = [0, 1]
        num_classes = 5
        
        model = DeepConvNet(input_dims=(C, H, W), num_filters=num_filters,
                           max_pools=max_pools, num_classes=num_classes,
                           dtype=self.dtype, device=self.device)
        
        X = torch.randn(N, C, H, W, dtype=self.dtype, device=self.device)
        y = torch.randint(0, num_classes, (N,), dtype=torch.long, device=self.device)
        
        loss, grads = model.loss(X, y)
        
        # Check that loss is a scalar
        self.assertEqual(loss.shape, (), "Loss should be a scalar")
        
        # Check that all gradients are computed
        for i in range(len(num_filters) + 1):
            self.assertIn('W%d' % (i+1), grads)
            self.assertIn('b%d' % (i+1), grads)
        
        print("DeepConvNet test passed!")
        
    def test_batchnorm_forward(self):
        """Test BatchNorm forward pass"""
        print("Testing BatchNorm.forward...")
        
        N, D = 4, 5
        x = torch.randn(N, D, dtype=self.dtype, device=self.device)
        gamma = torch.ones(D, dtype=self.dtype, device=self.device)
        beta = torch.zeros(D, dtype=self.dtype, device=self.device)
        
        # Training mode
        bn_param = {'mode': 'train'}
        out, cache = BatchNorm.forward(x, gamma, beta, bn_param)
        
        # Check output shape
        self.assertEqual(out.shape, x.shape, "BatchNorm output shape incorrect")
        
        # Check that output is normalized (mean ≈ 0, std ≈ 1)
        self.assertTrue(torch.allclose(out.mean(dim=0), torch.zeros(D, dtype=self.dtype), rtol=1e-3, atol=1e-4),
                       "BatchNorm output mean should be close to 0")
        
        print("BatchNorm.forward test passed!")
        
    def test_batchnorm_backward(self):
        """Test BatchNorm backward pass"""
        print("Testing BatchNorm.backward...")
        
        N, D = 4, 5
        x = torch.randn(N, D, dtype=self.dtype, device=self.device)
        gamma = torch.ones(D, dtype=self.dtype, device=self.device)
        beta = torch.zeros(D, dtype=self.dtype, device=self.device)
        
        # Forward pass
        bn_param = {'mode': 'train'}
        out, cache = BatchNorm.forward(x, gamma, beta, bn_param)
        
        # Backward pass
        dout = torch.randn_like(out)
        dx, dgamma, dbeta = BatchNorm.backward(dout, cache)
        
        # Check gradient shapes
        self.assertEqual(dx.shape, x.shape, "dx shape incorrect")
        self.assertEqual(dgamma.shape, gamma.shape, "dgamma shape incorrect")
        self.assertEqual(dbeta.shape, beta.shape, "dbeta shape incorrect")
        
        print("BatchNorm.backward test passed!")
        
    def test_spatial_batchnorm(self):
        """Test SpatialBatchNorm"""
        print("Testing SpatialBatchNorm...")
        
        N, C, H, W = 2, 3, 4, 4
        x = torch.randn(N, C, H, W, dtype=self.dtype, device=self.device)
        gamma = torch.ones(C, dtype=self.dtype, device=self.device)
        beta = torch.zeros(C, dtype=self.dtype, device=self.device)
        
        # Forward pass
        bn_param = {'mode': 'train'}
        out, cache = SpatialBatchNorm.forward(x, gamma, beta, bn_param)
        
        # Check output shape
        self.assertEqual(out.shape, x.shape, "SpatialBatchNorm output shape incorrect")
        
        # Backward pass
        dout = torch.randn_like(out)
        dx, dgamma, dbeta = SpatialBatchNorm.backward(dout, cache)
        
        # Check gradient shapes
        self.assertEqual(dx.shape, x.shape, "dx shape incorrect")
        self.assertEqual(dgamma.shape, gamma.shape, "dgamma shape incorrect")
        self.assertEqual(dbeta.shape, beta.shape, "dbeta shape incorrect")
        
        print("SpatialBatchNorm test passed!")
        
    def test_kaiming_initializer(self):
        """Test Kaiming initializer"""
        print("Testing kaiming_initializer...")
        
        # Test linear layer
        Din, Dout = 10, 20
        weight = kaiming_initializer(Din, Dout, relu=True, device=self.device, dtype=self.dtype)
        
        self.assertEqual(weight.shape, (Din, Dout), "Linear weight shape incorrect")
        
        # Test conv layer
        Din, Dout, K = 3, 16, 3
        weight = kaiming_initializer(Din, Dout, K=K, relu=True, device=self.device, dtype=self.dtype)
        
        self.assertEqual(weight.shape, (Dout, Din, K, K), "Conv weight shape incorrect")
        
        print("Kaiming initializer test passed!")


if __name__ == '__main__':
    unittest.main()