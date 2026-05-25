# CS336 Assignment 2: Systems and Parallelism

## Assignment Overview

This assignment focuses on gaining hands-on experience with improving single-GPU training speed and scaling training to multiple GPUs. Students will implement several systems-level optimizations for Transformer model training.

## Core Tasks and Functionality

### 1. Benchmarking and Profiling Harness

#### 1.1 End-to-End Benchmarking
- **Task**: Write a script to perform basic end-to-end benchmarking of forward and backward passes in the Transformer model
- **Requirements**:
  - Support initialization of a model with given hyperparameters (e.g., number of layers)
  - Generate a random batch of data
  - Run warm-up steps before measuring time
  - Time execution of multiple steps (forward only, or both forward and backward passes)
  - Call `torch.cuda.synchronize()` after each step to ensure accurate GPU timing measurements
  - Use Python `timeit` module for timing measurements
- **Deliverable**: A script that initializes a Transformer model with given hyperparameters, creates random batch data, and times forward and backward passes

#### 1.2 Model Configurations
The assignment uses the following model sizes for benchmarking (vocabulary size: 10,000, batch size: 4, varying context lengths):
- **small**: d_model=768, d_ff=3072, num_layers=12, num_heads=12
- **medium**: d_model=1024, d_ff=4096, num_layers=24, num_heads=16
- **large**: d_model=1280, d_ff=5120, num_layers=36, num_heads=20
- **xl**: d_model=1600, d_ff=6400, num_layers=48, num_heads=25
- **2.7B**: d_model=2560, d_ff=10240, num_layers=32, num_heads=32

### 2. Flash Attention 2 Triton Kernel

#### 2.1 Custom GPU Kernel Implementation
- **Task**: Optimize the self-attention operation with a custom GPU kernel using Triton
- **Background**: Standard PyTorch attention implementations may not be optimal for GPU performance. Flash Attention 2 provides a faster, memory-efficient implementation using custom GPU kernels.
- **Deliverable**: Implementation of Flash Attention 2 using Triton that outperforms a straightforward PyTorch implementation

### 3. Distributed Data Parallel (DDP) Training

#### 3.1 Multi-GPU Training
- **Task**: Implement distributed data parallel training to leverage multiple GPUs
- **Requirements**: Scale training across multiple GPUs using DDP, ensuring proper synchronization and communication between devices
- **Deliverable**: Implementation that enables training across multiple GPUs with proper data distribution and gradient synchronization

### 4. Optimizer State Sharding

#### 4.1 Sharded Optimizer Implementation
- **Task**: Implement a simplified version of optimizer state sharding to reduce per-rank memory consumption
- **Requirements**:
  - Create a Python class that wraps an arbitrary PyTorch `optim.Optimizer`
  - Shard optimizer states across ranks (approximately 1/world_size per rank)
  - Each rank's optimizer only handles a subset of parameters
  - After optimizer step, broadcast updated parameters to synchronize across ranks
  - Implement the following interface:
    - `__init__(self, params, optimizer_cls: Type[Optimizer], **kwargs)`: Initialize sharded state optimizer, sharding parameters across ranks
    - `step(self, closure, **kwargs)`: Call wrapped optimizer's step(), then synchronize with other ranks
    - `add_param_group(self, param_group: dict[str, Any])`: Add parameter group to sharded optimizer, handling parameter assignment among ranks
- **Deliverable**: Container class for optimizer state sharding that passes test suite

#### 4.2 Memory and Performance Analysis
- **Task**: Analyze the effect of optimizer state sharding on memory usage and runtime overhead
- **Requirements**:
  - Profile peak memory usage with and without optimizer state sharding
  - Measure training speed with and without sharding
  - Compare approach to ZeRO stage 1 (ZeRO-DP P_os)
- **Deliverable**: Analysis of memory savings and performance impact

