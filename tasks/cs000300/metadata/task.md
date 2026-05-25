# Lab 3: A Conditional Generative Model for Images

## Experiment Background

In the previous lab, we studied *unconditional* generation for toy, two-dimensional data distributions. In this lab, we will study *conditional* generation on *images* from the MNIST dataset of handwritten digits. Each MNIST image is not two dimensions but $32\times 32 = 1024$ dimensions. The nature of this more challenging setting requires special considerations:

1. To tackle *conditional* generation, we will employ *classifier-free guidance* (CFG), which allows us to condition the generation process on class labels (digits 0-9) while maintaining high perceptual quality.

2. To parameterize our learned vector field for high-dimensional image-valued data, a simple MLP will not suffice. Instead, we will adopt the *U-Net* architecture, which is specifically tailored toward images.

The goal is to build a generative model that can generate images of specific digits (e.g., "generate an image of the digit 8") rather than just generating any random digit.

## Core Tasks and Functionality

### Part 1: Getting a Feel for MNIST

- Familiarize yourself with the MNIST dataset of handwritten digits
- Experiment with adding noise to MNIST images using `GaussianConditionalProbabilityPath`
- Understand how images are transformed through the conditional probability path at different time steps

### Part 2: Classifier-Free Guidance

#### Question 2.1: Understanding Classifier-Free Guidance

- Understand the theoretical foundation of classifier-free guidance
- Learn how to combine conditional and unconditional models at inference time using the formula:
  $$\tilde{u}_t(x|y) = (1-w) u_t(x|\varnothing) + w u_t(x|y)$$
  where $w > 1$ is the guidance scale and $\varnothing$ represents the null label

#### Question 2.2: Training for Classifier-Free Guidance

**Task**: Implement the training objective $\mathcal{L}_{\text{CFM}}(\theta)$ in the `CFGTrainer.get_train_loss` method.

The training procedure should:
1. Sample an image $z$ and a label $y$ from $p_{\text{data}}$ (MNIST dataset)
2. With probability $\eta$, replace the label $y$ with the null label $\varnothing = 10$
3. Sample $t$ from $\mathcal{U}[0,1]$
4. Sample $x$ from the conditional probability path $p_t(x|z)$
5. Regress $u_t^{\theta}(x|y)$ against $u_t^{\text{ref}}(x|z)$

### Part 3: An Architecture for Images

#### Question 3.1: Building a U-Net

**Task**: Pick *two* components from the U-Net architecture (`FourierEncoder`, `ResidualLayer`, `Encoder`, `Decoder`, or `Midcoder`) and explain:
1. Their role in the U-Net
2. Their inputs and outputs
3. A brief description of how the inputs turn into outputs

The U-Net architecture consists of:
- **FourierEncoder**: Encodes time information using Fourier features
- **ResidualLayer**: Applies residual connections with time and label conditioning
- **Encoder**: Downsampling blocks that reduce spatial dimensions
- **Midcoder**: Middle processing blocks
- **Decoder**: Upsampling blocks that restore spatial dimensions

#### Question 3.2: Training a U-Net for Classifier-Free Guidance

- Train the U-Net model using the CFG training objective
- Evaluate the model's performance with different guidance scales
- Observe how increasing the guidance scale $w$ affects the quality and characteristics of generated samples
- Provide an intuitive explanation for why increasing the guidance scale has the observed effects

## Key Concepts

- **Conditional Generation**: Generating samples conditioned on specific labels (e.g., digit class)
- **Classifier-Free Guidance (CFG)**: A technique that combines conditional and unconditional models to improve generation quality
- **U-Net Architecture**: A convolutional neural network architecture with encoder-decoder structure and skip connections, well-suited for image processing tasks
- **Flow Matching**: A training objective for learning generative models by matching vector fields

