# Lab Two: Flow Matching and Score Matching

## Background

This lab provides an intuitive and hands-on walk-through of **flow matching** and **score matching**. The core idea is to learn a vector field that transforms a simple source distribution (e.g., a Gaussian) into a complex target distribution (e.g., a Gaussian mixture) through a continuous probability path.

The lab introduces two key concepts:

1. **Conditional Probability Paths**: A conditional probability path $p_t(x|z)$ interpolates between a simple distribution $p_{\text{simple}}$ at $t=0$ and a delta distribution $\delta_z$ at $t=1$. By averaging over conditioning variables $z \sim p_{\text{data}}$, we obtain a marginal probability path that bridges $p_{\text{simple}}$ to $p_{\text{data}}$.

2. **Flow Matching and Score Matching**: We learn approximations to the marginal vector field $u_t^{\text{ref}}(x)$ and marginal score $\nabla \log p_t(x)$ by regressing against their conditional counterparts, which are often analytically tractable.

## Core Tasks

### Part 1: Implementing Conditional Probability Paths

The lab introduces the abstract base class `ConditionalProbabilityPath` which defines the interface for conditional probability paths. Students will implement two concrete subclasses:

- `GaussianConditionalProbabilityPath`: Uses Gaussian conditional paths
- `LinearConditionalProbabilityPath`: Uses linear interpolation paths

### Part 2: Gaussian Conditional Probability Paths

#### Problem 2.1: Implementing $\alpha_t$ and $\beta_t$

**Task**: Implement the `__call__` methods for:
- `LinearAlpha`: Implements $\alpha_t = t$
- `SquareRootBeta`: Implements $\beta_t = \sqrt{1-t}$

These functions satisfy the boundary conditions: $\alpha_0 = \beta_1 = 0$ and $\alpha_1 = \beta_0 = 1$.

#### Problem 2.2: Gaussian Conditional Probability Path Sampling

**Task**: Implement `GaussianConditionalProbabilityPath.sample_conditional_path` to sample from the conditional distribution:
$$p_t(x|z) = N(x; \alpha_t z, \beta_t^2 I_d)$$

**Hint**: Use the fact that $X \sim N(\mu, \sigma^2 I_d)$ can be obtained via $X = \mu + \sigma Z$ where $Z \sim N(0, I_d)$.

#### Problem 2.3: Conditional Vector Field

**Task**: Implement `GaussianConditionalProbabilityPath.conditional_vector_field` to compute:
$$u_t(x|z) = \left(\dot{\alpha}_t - \frac{\dot{\beta}_t}{\beta_t}\alpha_t\right)z + \frac{\dot{\beta}_t}{\beta_t}x$$

**Hint**: Use `self.alpha.dt(t)` and `self.beta.dt(t)` to compute time derivatives.

#### Problem 2.4: Conditional Score

**Task**: Implement `GaussianConditionalProbabilityPath.conditional_score` to compute:
$$\nabla_x \log p_t(x|z) = \frac{\alpha_t z - x}{\beta_t^2}$$

### Part 3: Flow Matching and Score Matching with Gaussian Conditional Probability Paths

#### Problem 3.1: Flow Matching

**Task**: Implement `ConditionalFlowMatchingTrainer.get_train_loss` to compute the conditional flow matching objective:
$$\mathcal{L}_{\text{CFM}}(\theta) = \mathbb{E}_{t \sim \mathcal{U}[0,1), z \sim p(z), x \sim p_t(x|z)} \left[\lVert u_t^{\theta}(x) - u_t^{\text{ref}}(x|z)\rVert^2\right]$$

**Implementation steps**:
1. Sample `batch_size` points $z$ from $p_{\text{data}}$ using `self.path.p_data.sample(batch_size)`
2. Sample `batch_size` time values $t$ uniformly from $[0,1)$ using `torch.rand(batch_size, 1)`
3. Sample `batch_size` points from $p_t(x|z)$ using `self.path.sample_conditional_path(z,t)`
4. Compute the learned vector field $u_t^{\theta}(x)$ using `self.model(x,t)`
5. Compute the reference vector field $u_t^{\text{ref}}(x|z)$ using `self.path.conditional_vector_field(x,z,t)`
6. Return the mean squared error between the two

#### Problem 3.2: Score Matching

**Task**: Implement `ConditionalScoreMatchingTrainer.get_train_loss` to compute the conditional score matching loss:
$$\mathcal{L}_{\text{CSM}}(\theta) = \mathbb{E}_{t \sim \mathcal{U}[0,1), z \sim p(z), x \sim p_t(x|z)} \left[\lVert s_t^{\theta}(x) - \nabla \log p_t(x|z)\rVert^2\right]$$

**Implementation steps**: Similar to Problem 3.1, but:
- Use `self.model(x,t)` for the learned score $s_t^{\theta}(x)$
- Use `self.path.conditional_score(x,z,t)` for the reference conditional score

#### Problem 3.3: Deriving the Marginal Score from the Marginal Flow

**Task**: Implement `ScoreFromVectorField.forward` to compute the score parameterized via the learned vector field:
$$\tilde{s}_t^{\theta}(x) = \frac{u_t^{\theta}(x) - a_t x}{b_t} = \frac{\alpha_t u_t^{\theta}(x) - \dot{\alpha}_t x}{\beta_t^2 \dot{\alpha}_t - \alpha_t \dot{\beta}_t \beta_t}$$

where $(a_t, b_t) = \left(\frac{\dot{\alpha}_t}{\alpha_t}, \beta_t^2 \frac{\dot{\alpha}_t}{\alpha_t} - \dot{\beta}_t \beta_t\right)$.

For $\alpha_t = t$ and $\beta_t = \sqrt{1-t}$, we have:
$$\beta_t^2 \dot{\alpha}_t - \alpha_t \dot{\beta}_t \beta_t = 1 - \frac{t}{2}$$

### Part 4: Flow Matching Between Arbitrary Distributions with a Linear Probability Path

#### Problem 4.1: Linear Probability Paths

**Task**: Implement two methods for `LinearConditionalProbabilityPath`:

1. **`sample_conditional_path`**: Sample from the linear interpolant:
   $$X_t = (1-t) X_0 + t z$$
   where $X_0 \sim p_{\text{simple}}$ and $z$ is the conditioning variable.

2. **`conditional_vector_field`**: Compute the conditional vector field:
   $$u_t(x|z) = \frac{z - x}{1-t}$$

**Note**: The linear probability path does not have a closed-form expression for the conditional score, so `conditional_score` should raise an exception.

#### Problem 4.2: Flow Matching with Linear Probability Paths

**Task**: Train a flow matching model using the linear conditional probability path. The implementation from Problem 3.1 should work directly with `LinearConditionalProbabilityPath`.

#### Problem 4.3: Bridging Between Arbitrary Source and Target

**Task**: Experiment with different choices of $p_{\text{simple}}$ and $p_{\text{data}}$. The linear probability path allows for arbitrary source and target distributions, not just Gaussians.

**Available distributions**:
- `Gaussian.isotropic(dim, std)`: Isotropic Gaussian
- `GaussianMixture.symmetric_2D(nmodes, std, scale)`: Symmetric Gaussian mixture
- `MoonsSampleable(device, noise, scale)`: Two-moon distribution
- `CirclesSampleable(device, noise, scale)`: Concentric circles distribution
- `CheckerboardSampleable(device, grid_size, scale)`: Checkerboard pattern distribution

**Exploration**: Try different combinations and observe how the flow matching performs.

## Key Concepts

- **Conditional Probability Path**: $p_t(x|z)$ that interpolates between $p_{\text{simple}}$ and $\delta_z$
- **Marginal Probability Path**: $p_t(x) = \int p_t(x|z) p(z) dz$ that bridges $p_{\text{simple}}$ to $p_{\text{data}}$
- **Conditional Vector Field**: $u_t^{\text{ref}}(x|z)$ that generates the conditional probability path via an ODE
- **Marginal Vector Field**: $u_t^{\text{ref}}(x) = \mathbb{E}_{z \sim p_t(z|x)}[u_t^{\text{ref}}(x|z)]$
- **Flow Matching**: Learning $u_t^{\theta}(x) \approx u_t^{\text{ref}}(x)$ by regressing against conditional vector fields
- **Score Matching**: Learning $s_t^{\theta}(x) \approx \nabla \log p_t(x)$ by regressing against conditional scores
- **Langevin Dynamics**: Adding stochasticity to ODEs while preserving marginals: $dX_t = [u_t(x) + \frac{1}{2}\sigma^2 \nabla \log p_t(x)] dt + \sigma dW_t$

