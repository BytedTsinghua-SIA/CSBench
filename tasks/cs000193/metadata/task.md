## Task Instructions

### Task Source

EECS 498-007 / 598-005
Deep Learning for Computer Vision

### Task Overview

In this assignment, you will implement Fully-Connected Neural Networks and Convolutional Neural Networks for image classification models. The goals of this assignment are as follows:

- Understand Neural Networks and how they are arranged in layered architectures
- Understand and be able to implement modular backpropagation
- Implement various update rules used to optimize Neural Networks
- Implement Batch Normalization for training deep networks
- Implement Dropout to regularize networks
- Understand the architecture of Convolutional Neural Networks and get practice with training these models on data

### Detailed Requirements

#### Fully Connected Networks

**Core Functions and Classes:**

1. **Basic Layer Functions:**
   - `hello_fully_connected_networks()` - Environment test function
   - `Linear.forward(x, w, b)` - Linear layer forward pass
   - `Linear.backward(dout, cache)` - Linear layer backward pass
   - `ReLU.forward(x)` - ReLU activation forward pass
   - `ReLU.backward(dout, cache)` - ReLU activation backward pass
   - `Linear_ReLU.forward(x, w, b)` - Linear+ReLU combined layer forward pass
   - `Linear_ReLU.backward(dout, cache)` - Linear+ReLU combined layer backward pass

2. **Network Model Classes:**
   - `TwoLayerNet.__init__(...)` - Two-layer neural network initialization
   - `TwoLayerNet.save(path)` - Model saving
   - `TwoLayerNet.load(path, dtype, device)` - Model loading
   - `TwoLayerNet.loss(X, y)` - Loss function computation
   - `FullyConnectedNet.__init__(...)` - Multi-layer fully connected network initialization
   - `FullyConnectedNet.save(path)` - Model saving
   - `FullyConnectedNet.load(path, dtype, device)` - Model loading
   - `FullyConnectedNet.loss(X, y)` - Loss function computation

3. **Optimization Algorithm Functions:**
   - `sgd(w, dw, config)` - Stochastic Gradient Descent
   - `sgd_momentum(w, dw, config)` - SGD with Momentum
   - `rmsprop(w, dw, config)` - RMSProp optimizer
   - `adam(w, dw, config)` - Adam optimizer

4. **Regularization Functions:**
   - `Dropout.forward(x, dropout_param)` - Dropout forward pass
   - `Dropout.backward(dout, cache)` - Dropout backward pass

5. **Helper Functions:**
   - `create_solver_instance(data_dict, dtype, device)` - Create solver instance
   - `get_three_layer_network_params()` - Get three-layer network parameters
   - `get_five_layer_network_params()` - Get five-layer network parameters

#### Convolutional Networks

**Core Functions and Classes:**

1. **Basic Layer Functions:**
   - `hello_convolutional_networks()` - Environment test function
   - `Conv.forward(x, w, b, conv_param)` - Convolutional layer forward pass
   - `Conv.backward(dout, cache)` - Convolutional layer backward pass
   - `MaxPool.forward(x, pool_param)` - Max pooling layer forward pass
   - `MaxPool.backward(dout, cache)` - Max pooling layer backward pass

2. **Network Model Classes:**
   - `ThreeLayerConvNet.__init__(...)` - Three-layer convolutional network initialization
   - `ThreeLayerConvNet.save(path)` - Model saving
   - `ThreeLayerConvNet.load(path)` - Model loading
   - `ThreeLayerConvNet.loss(X, y)` - Loss function computation
   - `DeepConvNet.__init__(...)` - Deep convolutional network initialization
   - `DeepConvNet.save(path)` - Model saving
   - `DeepConvNet.load(path, dtype, device)` - Model loading
   - `DeepConvNet.loss(X, y)` - Loss function computation

3. **Batch Normalization Functions:**
   - `BatchNorm.forward(x, gamma, beta, bn_param)` - Batch normalization forward pass
   - `BatchNorm.backward(dout, cache)` - Batch normalization backward pass
   - `BatchNorm.backward_alt(dout, cache)` - Alternative batch normalization backward pass
   - `SpatialBatchNorm.forward(x, gamma, beta, bn_param)` - Spatial batch normalization forward pass
   - `SpatialBatchNorm.backward(dout, cache)` - Spatial batch normalization backward pass

4. **Fast Implementations and Sandwich Layers:**
   - `FastConv.forward(x, w, b, conv_param)` - Fast convolution forward pass
   - `FastConv.backward(dout, cache)` - Fast convolution backward pass
   - `FastMaxPool.forward(x, pool_param)` - Fast max pooling forward pass
   - `FastMaxPool.backward(dout, cache)` - Fast max pooling backward pass
   - `Conv_ReLU.forward(x, w, b, conv_param)` - Conv+ReLU combined layer forward pass
   - `Conv_ReLU.backward(dout, cache)` - Conv+ReLU combined layer backward pass
   - `Conv_ReLU_Pool.forward(x, w, b, conv_param, pool_param)` - Conv+ReLU+Pool combined layer forward pass
   - `Conv_ReLU_Pool.backward(dout, cache)` - Conv+ReLU+Pool combined layer backward pass
   - `Linear_BatchNorm_ReLU.forward(x, w, b, gamma, beta, bn_param)` - Linear+BatchNorm+ReLU combined layer forward pass
   - `Linear_BatchNorm_ReLU.backward(dout, cache)` - Linear+BatchNorm+ReLU combined layer backward pass
   - `Conv_BatchNorm_ReLU.forward(x, w, b, gamma, beta, conv_param, bn_param)` - Conv+BatchNorm+ReLU combined layer forward pass
   - `Conv_BatchNorm_ReLU.backward(dout, cache)` - Conv+BatchNorm+ReLU combined layer backward pass
   - `Conv_BatchNorm_ReLU_Pool.forward(x, w, b, gamma, beta, conv_param, bn_param, pool_param)` - Conv+BatchNorm+ReLU+Pool combined layer forward pass
   - `Conv_BatchNorm_ReLU_Pool.backward(dout, cache)` - Conv+BatchNorm+ReLU+Pool combined layer backward pass

5. **Helper Functions:**
   - `find_overfit_parameters()` - Find overfitting parameters
   - `create_convolutional_solver_instance(data_dict, dtype, device)` - Create convolutional solver instance
   - `kaiming_initializer(Din, Dout, K, relu, device, dtype)` - Kaiming initializer
