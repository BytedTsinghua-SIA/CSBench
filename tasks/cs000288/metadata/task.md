# CS336 Assignment 3: Scaling Laws

## Assignment Overview

This assignment focuses on gaining hands-on experience with language model scaling laws. The goal is to determine the optimal model size and training hyperparameters for a given compute budget by fitting scaling laws and extrapolating to larger scales.

### Background

You are tasked with training ClosedAI's next-generation language model. Given a fixed compute budget (measured in FLOPs), the objective is to produce a model with the lowest training loss (i.e., a compute-optimal model). This requires determining the best tradeoff between (1) training a larger model versus (2) training on more tokens.

Scaling laws empirically relate language model training loss to model size and the amount of compute used for training. In this assignment, you will construct scaling laws to estimate the compute-optimal model size and corresponding hyperparameters for a FLOPs budget of 1e19.

## Core Tasks

### Problem 1: IsoFLOPs Method (chinchilla_isoflops)

**Objective**: Reproduce the IsoFLOPs method for fitting scaling laws using training loss data from synthetic runs.

**Deliverables**:
1. A script that:
   - Reads training run data from `data/isoflops_curves.json`
   - For each compute budget, finds the model size that minimizes training loss
   - Fits power laws: \(N_{opt} \propto C^a\) and \(D_{opt} \propto C^b\)
   - Extrapolates compute-optimal model and dataset sizes to target budgets

2. A plot showing the scaling law for model size by compute budget, including:
   - Data points used to fit the scaling law
   - Extrapolation up to at least \(10^{24}\) FLOPs
   - One-sentence response with predicted optimal model size for \(10^{23}\) and \(10^{24}\) FLOPs

3. A plot showing the scaling law for dataset size by compute budget, including:
   - Data points used to fit the scaling law
   - Extrapolation up to at least \(10^{24}\) FLOPs
   - One-sentence response with predicted optimal dataset size for \(10^{23}\) and \(10^{24}\) FLOPs

**Data Format**: The `data/isoflops_curves.json` file contains a JSON array where each element has:
- `parameters`: Number of model parameters
- `compute_budget`: FLOPs used (e.g., 6e18)
- `final_loss`: Final training loss

**Implementation Notes**:
- Use `scipy.optimize.curve_fit` or similar for curve fitting
- For each compute budget, simply take the run with the lowest training loss as the minimum (rather than fitting a quadratic)

### Problem 2: Constructing Scaling Laws

**Objective**: Construct your own scaling laws using a training API to predict the optimal model configuration for a compute budget of 1e19 FLOPs.

**Compute Budget**: 
- Training API budget: 2e18 FLOPs (20% of the target budget of 1e19) for fitting scaling laws
- Target budget: 1e19 FLOPs for the final optimal model

**Training API Details**:

The API endpoint `GET /loss` accepts the following parameters:
- `d_model`: Integer in [64, 1024]
- `num_layers`: Integer in [2, 24]
- `num_heads`: Integer in [2, 16]
- `batch_size`: Integer, one of {128, 256}
- `learning_rate`: Float in [1e-3, 1e-4]
- `train_flops`: Integer, one of {1e13, 3e13, 6e13, 1e14, 3e14, 6e14, 1e15, 3e15, 6e15, 1e16, 3e16, 6e16, 1e17, 3e17, 6e17, 1e18}
- `api_key`: Your API key string

Returns:
- `loss`: Float training loss
- `total_flops_used`: Total FLOPs used across all queries

**Additional API Endpoints**:
- `GET /total_flops_used`: Returns total FLOPs used for your API key
- `GET /previous_runs`: Returns all previous runs queried with your API key

**Model Architecture Details**:
- Transformer language model with absolute position embeddings (not RoPE)
- Layer normalization (not RMSNorm)
- Feedforward networks: linear → GeLU → linear, with \(d_{ff} = 4d_{model}\)
- Untied input and output embeddings
- Attention and residual dropout (probability 0.1)
- Context length: 512 tokens
- Vocabulary: 32K (byte-level BPE tokenizer)
- Training: AdamW optimizer, weight decay 0.01, gradient clipping 1.0
- Learning rate: Cosine schedule (decay by 10×, no warm-up)

**Parameter Count Formula**: For estimating non-embedding parameters:
\[N = 12n_{\text{layer}}d_{\text{model}}^{2}\]

**Deliverables**:
1. A complete methodology description covering:
   - How you explored the hyperparameter search space
   - The method(s) used to fit your scaling law (reference Kaplan et al., 2020 and Hoffmann et al., 2022 approaches)
   - How well your scaling law fits the experimental data
   - For a FLOPs budget of 1e19:
     - Predicted optimal model size
     - Predicted training loss
     - Training hyperparameters to use (including batch size 128 or 256)

2. Submission to Google Form with:
   - Predicted optimal model size
   - Training hyperparameters (including batch size 128 or 256)
   - Predicted training loss

## Key Constraints

- You must efficiently use the 2e18 FLOPs budget for fitting scaling laws
- The training API accepts a wide range of hyperparameters; you must determine which parts of the search space to explore
- Previously-queried experimental configurations do not incur extra FLOPs toward your budget
- API queries require being on the Stanford network (VPN may be required)

## References

- Kaplan et al. (2020): Scaling laws for neural language models
- Hoffmann et al. (2022): Training compute-optimal large language models (Chinchilla)
- Yang et al. (2022): Tensor Programs V: Tuning large neural networks via zero-shot hyperparameter transfer

