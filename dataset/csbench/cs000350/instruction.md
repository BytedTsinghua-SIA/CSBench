# Project 4: Ghostbusters

## Background

In the CS 188 version of Ghostbusters, the goal is to hunt down scared but invisible ghosts. Pacman, ever resourceful, is equipped with sonar (ears) that provides noisy readings of the Manhattan distance to each ghost. The game ends when Pacman has eaten all the ghosts.

The noisy distances at the bottom of the display are always non-negative, and always within 7 of the true distance. The probability of a distance reading decreases exponentially with its difference from the true distance.

The primary task in this project is to implement inference to track the ghosts. Throughout the project, you will implement algorithms for performing both exact and approximate inference using Bayes Nets.

## Core Tasks

### Question 1 (2 points): Bayes Net Structure
Implement the Bayes Net structure for the ghost tracking problem.

### Question 2 (3 points): Join Factors
Implement the `joinFactors` function to combine factors in the Bayes Net.

### Question 3 (2 points): Eliminate
Implement the `eliminate` function to eliminate variables from factors.

### Question 4 (2 points): Variable Elimination
Implement variable elimination algorithm to compute marginal probabilities.

### Question 5a: DiscreteDistribution Class
Implement the `DiscreteDistribution` class for representing probability distributions.

### Question 5b (1 point): Observation Probability
Implement observation probability calculation given Pacman's position and potential ghost position.

### Question 6 (2 points): Exact Inference Observation
Implement the `observeUpdate` method in the `ExactInference` class. This method should update the belief distribution for a ghost based on a new observation.

### Question 7 (2 points): Exact Inference with Time Elapse
Implement the `elapseTime` method in the `ExactInference` class. This method should update the belief at every position on the map after one time step elapsing, using the ghost's action distribution.

### Question 8 (1 point): Exact Inference Full Test
Implement the `chooseAction` method in `GreedyBustersAgent`. The agent should find the most likely position of each remaining uncaptured ghost, then choose an action that minimizes the maze distance to the closest ghost.

### Question 9 (1 point): Approximate Inference Initialization and Beliefs
Implement the functions `initializeUniformly` and `getBeliefDistribution` in the `ParticleFilter` class. Particles should be evenly distributed across legal positions to ensure a uniform prior.

### Question 10 (2 points): Approximate Inference Observation
Implement the `observeUpdate` method in the `ParticleFilter` class. This method constructs a weight distribution over particles based on observation probability, then resamples from this weighted distribution.

### Question 11 (2 points): Approximate Inference with Time Elapse
Implement the `elapseTime` function in the `ParticleFilter` class. This function should construct a new list of particles that corresponds to each existing particle advancing a time step.

## Key Concepts

- **Bayes Nets**: Probabilistic graphical models for representing and reasoning about uncertainty
- **Exact Inference**: Computing exact probability distributions using variable elimination
- **Approximate Inference**: Using particle filtering to approximate probability distributions
- **Hidden Markov Models**: Modeling the ghost tracking problem where ghost positions are hidden states
- **Observation Model**: Noisy distance readings that provide evidence about ghost locations
- **Transition Model**: How ghost positions change over time based on their movement patterns

