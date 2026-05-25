## Task Instructions

### Task Source

UC Berkeley CS285: Deep Reinforcement Learning - Homework 2 (Policy Gradients)

### Task Overview

This task involves implementing a Policy Gradient (PG) agent for reinforcement learning. The PG agent uses policy gradient methods to learn a policy that maximizes expected cumulative reward. Key components include computing Q-values using trajectory-based and reward-to-go estimators, estimating advantages with optional baseline and GAE (Generalized Advantage Estimation), and updating the policy network accordingly.

### Files to Modify

The following files need to be modified to complete this task:

1. **`pg_agent.py`**
   - `train` method
   - `calculate_q_vals` method
   - `estimate_advantage` method
   - `_discounted_return` helper function
   - `_discounted_cumsum` helper function

2. **`MLP_policy.py`**
   - `get_action` method
   - `forward` method (for continuous actions)
   - `update` method in `MLPPolicyPG` class

### Detailed Requirements

1. **`train` method**: Update the PG actor/policy using the given batch of data. This involves:
   - Computing Q-values from rewards using `calculate_q_vals`
   - Computing advantages using `estimate_advantage`
   - Calling the actor's `update` method with observations, actions, advantages, and Q-values
   - Returning the training log

2. **`calculate_q_vals` method**: Monte Carlo estimation of the Q function.
   - **Trajectory-based PG** (when `reward_to_go=False`): Estimate Q(s_t, a_t) using the total discounted reward from the entire trajectory.
     - Formula: Q(s_t, a_t) = sum_{t'=0}^T gamma^t' * r_{t'}
     - All timesteps in the same trajectory share the same Q value
   - **Reward-to-go PG** (when `reward_to_go=True`): Estimate Q(s_t, a_t) as the discounted sum of rewards starting from time t.
     - Formula: Q(s_t, a_t) = sum_{t'=t}^T gamma^(t'-t) * r_{t'}
     - Each timestep has a different Q value
   - Use helper functions `_discounted_return` and `_discounted_cumsum`
   - Return a flattened 1D numpy array

3. **`estimate_advantage` method**: Compute advantages by (optionally) subtracting a baseline from Q values.
   - **With neural network baseline** (`nn_baseline=True`):
     - Query the baseline network to get value predictions
     - Denormalize values to match the scale of Q-values
     - Compute advantages as: advantages = Q - values
     - **With GAE** (`gae_lambda` is not None):
       - Use Generalized Advantage Estimation formula:
         - A_t = delta_t + gamma * lambda * A_{t+1}
         - Where delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)
         - Handle terminal states using the `terminals` array
   - **Without baseline**: Set advantages = Q values
   - **Standardization**: If `standardize_advantages` is True, normalize advantages to have mean=0 and std=1

4. **`_discounted_return` helper function**: Compute the discounted return for a trajectory.
   - Input: list of rewards from a single rollout
   - Output: list where each index t contains the total discounted return (same for all timesteps in trajectory)
   - Formula: sum_{t'=0}^T gamma^t' * r_{t'}
   - Handle empty input gracefully (return empty list)

5. **`_discounted_cumsum` helper function**: Compute reward-to-go discounted cumulative sum.
   - Input: list of rewards from a single rollout
   - Output: list where index t' contains sum_{t'=t}^T gamma^(t'-t) * r_{t'}
   - Handle empty input gracefully (return empty list)

### Mathematical Formulas

**Trajectory-based Q-value:**
```
Q^{pi}(s_t, a_t) = sum_{t'=0}^{T-1} gamma^t' * r_{t'}
```
All timesteps share the same Q value (total discounted return of the trajectory).

**Reward-to-go Q-value:**
```
Q^{pi}(s_t, a_t) = sum_{t'=t}^{T-1} gamma^(t'-t) * r_{t'}
```
Each timestep has a different Q value based on remaining rewards.

**GAE Advantage Estimation:**
```
A_t^{GAE(gamma, lambda)} = sum_{l=0}^{infty} (gamma * lambda)^l * delta_{t+l}
```
Where delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)

### Implementation Hints

1. For `_discounted_return`:
   - Compute the cumulative sum of discounted rewards from the full trajectory
   - The total return is the same for all timesteps in the trajectory
   - Return `[total_return] * len(rewards)`

2. For `_discounted_cumsum`:
   - Iterate backwards through the rewards
   - At each step, compute cumulative sum from that point forward
   - Use gamma discounting: cumsum = reward[i] + gamma * cumsum

3. For advantage normalization:
   - Use (adv - mean) / (std + 1e-8) to prevent division by zero

4. For GAE:
   - Handle terminal states by setting advantage at terminal to just the reward minus value
   - Use reversed iteration to compute advantages backwards in time

### Testing

The implementation will be tested with:
- Various reward sequences including empty, single-element, and multi-element
- Different gamma values (0, 0.99, 1.0)
- Both positive and negative rewards
- Multiple trajectories
- Proper handling of NaN/edge cases in normalization
