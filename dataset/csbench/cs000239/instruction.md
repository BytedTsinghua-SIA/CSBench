## Task Instructions

https://github.com/berkeleydeeprlcourse/homework_fall2022/tree/main/hw1

### Task Source

UC Berkeley CS285: Deep Reinforcement Learning, Decision Making, and Control - Homework 1: Imitation Learning

### Task Overview

This assignment implements imitation learning algorithms for continuous control tasks using PyTorch. The goal is to learn policies from expert demonstrations through Behavioral Cloning and DAgger (Dataset Aggregation) algorithms. Students will implement core components of the reinforcement learning infrastructure, including policy networks, replay buffers, and training loops, and apply them to MuJoCo environments.

### Detailed Requirements

1. **Behavioral Cloning (BC)**: Implement supervised learning from expert demonstrations.
   - Complete the `MLPPolicySL` class with `forward`, `update`, and `get_action` methods
   - Implement the `BCAgent` class with training and sampling methods
   - Run BC on Ant-v4 environment and achieve at least 30% of expert performance

2. **DAgger Algorithm**: Implement iterative dataset aggregation with expert relabeling.
   - Complete the `do_relabel_with_expert` method in `rl_trainer.py`
   - Implement the data collection and expert querying loop
   - Compare DAgger performance with Behavioral Cloning

3. **Infrastructure Implementation**:
   - **Replay Buffer**: Implement `ReplayBuffer` class with `add_rollouts` and `sample_random_data` methods
   - **Policy Networks**: Implement `MLPPolicy` base class and `MLPPolicySL` subclass
   - **Training Utilities**: Complete `collect_training_trajectories`, `train_agent` methods in `rl_trainer.py`
   - **PyTorch Utilities**: Implement `build_mlp` function for neural network construction

4. **Code Structure**:
   - `cs285/infrastructure/rl_trainer.py`: Main training loop and data collection
   - `cs285/policies/MLP_policy.py`: Policy network implementations
   - `cs285/infrastructure/replay_buffer.py`: Experience replay buffer
   - `cs285/infrastructure/pytorch_util.py`: PyTorch utility functions
   - `cs285/infrastructure/utils.py`: Trajectory sampling utilities

5. **Experimentation**:
   - Run Behavioral Cloning on at least two MuJoCo environments (e.g., Ant-v4, Hopper-v4)
   - Implement DAgger and compare learning curves with BC
   - Analyze the effect of different hyperparameters (batch size, learning rate, network architecture)
   - Generate plots comparing expert, BC, and DAgger performance

6. **Testing Requirements**:
   - All implemented components must pass the provided test suite
   - Tests cover policy creation, forward passes, replay buffer operations, and integration
   - Code should handle both discrete and continuous action spaces
   - Proper error handling for edge cases (e.g., empty replay buffer)