# CS336 Assignment 1: Building a Transformer Language Model

## Assignment Overview

In this assignment, you will build all the components needed to train a standard Transformer language model (LM) from scratch and train some models.

### What You Will Implement

1. Byte-pair encoding (BPE) tokenizer
2. Transformer language model (LM)
3. The cross-entropy loss function and the AdamW optimizer
4. The training loop, with support for serializing and loading model and optimizer state

### What You Will Run

1. Train a BPE tokenizer on the TinyStories dataset
2. Run your trained tokenizer on the dataset to convert it into a sequence of integer IDs
3. Train a Transformer LM on the TinyStories dataset
4. Generate samples and evaluate perplexity using the trained Transformer LM
5. Train models on OpenWebText and submit your attained perplexities to a leaderboard

### Constraints

You are expected to build these components from scratch. In particular, you may not use any definitions from `torch.nn`, `torch.nn.functional`, or `torch.optim` except for:

- `torch.nn.Parameter`
- Container classes in `torch.nn` (e.g., Module, ModuleList, Sequential, etc.)
- The `torch.optim.Optimizer` base class

You may use any other PyTorch definitions.

---

## Part 2: Byte-Pair Encoding (BPE) Tokenizer

### Background

In this part, you will train and implement a byte-level byte-pair encoding (BPE) tokenizer. You will represent arbitrary (Unicode) strings as a sequence of bytes and train the BPE tokenizer on this byte sequence. Later, you will use this tokenizer to encode text (a string) into tokens (a sequence of integers) for language modeling.

### Problem 2.1: Understanding Unicode (1 point)

(a) What Unicode character does `chr(0)` return?  
Deliverable: A one-sentence response.

(b) How does this character's string representation (`__repr__()`) differ from its printed representation?  
Deliverable: A one-sentence response.

(c) What happens when this character occurs in text?  
Deliverable: A one-sentence response.

### Problem 2.2: Unicode Encodings (3 points)

(a) What are some reasons to prefer training our tokenizer on UTF-8 encoded bytes, rather than UTF-16 or UTF-32?  
Deliverable: A one-to-two sentence response.

(b) Consider the following (incorrect) function, which is intended to decode a UTF-8 byte string into a Unicode string. Why is this function incorrect? Provide an example of an input byte string that yields incorrect results.

```python
def decode_utf8_bytes_to_str_wrong(bytestring: bytes):
    return "".join([bytes([b]).decode("utf-8") for b in bytestring])
```

Deliverable: An example input byte string for which `decode_utf8_bytes_to_str_wrong` produces incorrect output, with a one-sentence explanation of why the function is incorrect.

(c) Give a two byte sequence that does not decode to any Unicode character(s).  
Deliverable: An example, with a one-sentence explanation.

### Problem 2.3: BPE Tokenizer Training (15 points)

**Deliverable:** Write a function that, given a path to an input text file, trains a (byte-level) BPE tokenizer. Your BPE training function should handle (at least) the following input parameters:

- `input_path: str` - Path to a text file with BPE tokenizer training data
- `vocab_size: int` - A positive integer that defines the maximum final vocabulary size (including the initial byte vocabulary, vocabulary items produced from merging, and any special tokens)
- `special_tokens: list[str]` - A list of strings to add to the vocabulary. These special tokens do not otherwise affect BPE training

Your BPE training function should return the resulting vocabulary and merges:

- `vocab: dict[int, bytes]` - The tokenizer vocabulary, a mapping from int (token ID in the vocabulary) to bytes (token bytes)
- `merges: list[tuple[bytes, bytes]]` - A list of BPE merges produced from training. Each list item is a tuple of bytes (`<token1>`, `<token2>`), representing that `<token1>` was merged with `<token2>`. The merges should be ordered by order of creation

**Key Implementation Details:**

- Use the GPT-2 regex pattern for pre-tokenization: `r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""`
- Use `re.finditer` to avoid storing pre-tokenized words
- Remove special tokens before pre-tokenization, splitting on special tokens so no merging occurs across document boundaries
- For efficiency, use incremental pair counting rather than recounting all pairs after each merge
- Break ties in pair frequency by preferring the lexicographically greater pair
- You can parallelize pre-tokenization using multiprocessing

To test your BPE training function, implement the test adapter at `adapters.run_train_bpe`, then run `uv run pytest tests/test_train_bpe.py`.

### Problem 2.4: BPE Training on TinyStories (2 points)

(a) Train a byte-level BPE tokenizer on the TinyStories dataset, using a maximum vocabulary size of 10,000. Make sure to add the TinyStories `<|endoftext|>` special token to the vocabulary. Serialize the resulting vocabulary and merges to disk for further inspection. How many hours and memory did training take? What is the longest token in the vocabulary? Does it make sense?  
Resource requirements: ≤ 30 minutes (no GPUs), ≤ 30GB RAM  
Deliverable: A one-to-two sentence response.

(b) Profile your code. What part of the tokenizer training process takes the most time?  
Deliverable: A one-to-two sentence response.

### Problem 2.5: BPE Training on OpenWebText (2 points)

(a) Train a byte-level BPE tokenizer on the OpenWebText dataset, using a maximum vocabulary size of 32,000. Serialize the resulting vocabulary and merges to disk for further inspection. What is the longest token in the vocabulary? Does it make sense?  
Resource requirements: ≤ 12 hours (no GPUs), ≤ 100GB RAM  
Deliverable: A one-to-two sentence response.

(b) Compare and contrast the tokenizer that you get training on TinyStories versus OpenWebText.  
Deliverable: A one-to-two sentence response.

### Problem 2.6: Implementing the Tokenizer (15 points)

**Deliverable:** Implement a `Tokenizer` class that, given a vocabulary and a list of merges, encodes text into integer IDs and decodes integer IDs into text. Your tokenizer should also support user-provided special tokens (appending them to the vocabulary if they aren't already there).

**Recommended interface:**

```python
def __init__(self, vocab, merges, special_tokens=None)
    # Construct a tokenizer from a given vocabulary, list of merges, and (optionally) a list of special tokens
    # Parameters:
    #   vocab: dict[int, bytes]
    #   merges: list[tuple[bytes, bytes]]
    #   special_tokens: list[str] | None = None

@classmethod
def from_files(cls, vocab_filepath, merges_filepath, special_tokens=None)
    # Class method that constructs and returns a Tokenizer from serialized vocabulary and list of merges
    # Parameters:
    #   vocab_filepath: str
    #   merges_filepath: str
    #   special_tokens: list[str] | None = None

def encode(self, text: str) -> list[int]
    # Encode an input text into a sequence of token IDs

def encode_iterable(self, iterable: Iterable[str]) -> Iterator[int]
    # Given an iterable of strings (e.g., a Python file handle), return a generator that lazily yields token IDs
    # Required for memory-efficient tokenization of large files

def decode(self, ids: list[int]) -> str
    # Decode a sequence of token IDs into text
    # Note: If input token IDs do not produce a valid Unicode string, replace malformed bytes with U+FFFD
```

**Key Implementation Details:**

- Encoding: Pre-tokenize, then apply merges in the same order as during training
- Handle special tokens properly during encoding
- For `encode_iterable`, ensure tokens don't cross chunk boundaries
- For `decode`, use `errors='replace'` when decoding bytes to handle malformed sequences

To test your Tokenizer, implement the test adapter at `adapters.get_tokenizer`, then run `uv run pytest tests/test_tokenizer.py`.

### Problem 2.7: Experiments with Tokenizers (4 points)

(a) Sample 10 documents from TinyStories and OpenWebText. Using your previously-trained TinyStories and OpenWebText tokenizers (10K and 32K vocabulary size, respectively), encode these sampled documents into integer IDs. What is each tokenizer's compression ratio (bytes/token)?  
Deliverable: A one-to-two sentence response.

(b) What happens if you tokenize your OpenWebText sample with the TinyStories tokenizer? Compare the compression ratio and/or qualitatively describe what happens.  
Deliverable: A one-to-two sentence response.

(c) Estimate the throughput of your tokenizer (e.g., in bytes/second). How long would it take to tokenize the Pile dataset (825GB of text)?  
Deliverable: A one-to-two sentence response.

(d) Using your TinyStories and OpenWebText tokenizers, encode the respective training and development datasets into a sequence of integer token IDs. We recommend serializing the token IDs as a NumPy array of datatype `uint16`. Why is `uint16` an appropriate choice?  
Deliverable: A one-to-two sentence response.

---

## Part 3: Transformer Language Model Architecture

### Background

A language model takes as input a batched sequence of integer token IDs (i.e., `torch.Tensor` of shape `(batch_size, sequence_length)`), and returns a (batched) normalized probability distribution over the vocabulary (i.e., a PyTorch Tensor of shape `(batch_size, sequence_length, vocab_size)`), where the predicted distribution is over the next word for each input token.

The Transformer language model uses an input embedding to convert token IDs to dense vectors, passes the embedded tokens through `num_layers` Transformer blocks, and then applies a learned linear projection (the "output embedding" or "LM head") to produce the predicted next-token logits.

### Problem 3.1: Implementing the Linear Module (1 point)

**Deliverable:** Implement a `Linear` class that inherits from `torch.nn.Module` and performs a linear transformation. Your implementation should follow the interface of PyTorch's built-in `nn.Linear` module, except for not having a bias argument or parameter.

**Recommended interface:**

```python
def __init__(self, in_features, out_features, device=None, dtype=None)
    # Construct a linear transformation module
    # Parameters:
    #   in_features: int - final dimension of the input
    #   out_features: int - final dimension of the output
    #   device: torch.device | None = None
    #   dtype: torch.dtype | None = None

def forward(self, x: torch.Tensor) -> torch.Tensor
    # Apply the linear transformation to the input
```

**Requirements:**

- Subclass `nn.Module` and call the superclass constructor
- Construct and store your parameter as `W` (not `W^T`) for memory ordering reasons, putting it in an `nn.Parameter`
- Initialize weights using truncated normal: `N(μ=0, σ²=(d_in + d_out)/2)` truncated at `[-3σ, 3σ]`
- Use `torch.nn.init.trunc_normal_` for initialization
- Do not use `nn.Linear` or `nn.functional.linear`

To test your Linear module, implement the test adapter at `adapters.run_linear`, then run `uv run pytest -k test_linear`.

### Problem 3.2: Implement the Embedding Module (1 point)

**Deliverable:** Implement the `Embedding` class that inherits from `torch.nn.Module` and performs an embedding lookup. Your implementation should follow the interface of PyTorch's built-in `nn.Embedding` module.

**Recommended interface:**

```python
def __init__(self, num_embeddings, embedding_dim, device=None, dtype=None)
    # Construct an embedding module
    # Parameters:
    #   num_embeddings: int - Size of the vocabulary
    #   embedding_dim: int - Dimension of the embedding vectors, i.e., d_model
    #   device: torch.device | None = None
    #   dtype: torch.dtype | None = None

def forward(self, token_ids: torch.Tensor) -> torch.Tensor
    # Lookup the embedding vectors for the given token IDs
```

**Requirements:**

- Subclass `nn.Module` and call the superclass constructor
- Initialize your embedding matrix as a `nn.Parameter`
- Store the embedding matrix with the `d_model` being the final dimension
- Initialize embeddings using truncated normal: `N(μ=0, σ²=1)` truncated at `[-3, 3]`
- Use `torch.nn.init.trunc_normal_` for initialization
- Do not use `nn.Embedding` or `nn.functional.embedding`

To test your implementation, implement the test adapter at `adapters.run_embedding`, then run `uv run pytest -k test_embedding`.

### Problem 3.3: Root Mean Square Layer Normalization (1 point)

**Deliverable:** Implement `RMSNorm` as a `torch.nn.Module`.

**Recommended interface:**

```python
def __init__(self, d_model: int, eps: float = 1e-5, device=None, dtype=None)
    # Construct the RMSNorm module
    # Parameters:
    #   d_model: int - Hidden dimension of the model
    #   eps: float = 1e-5 - Epsilon value for numerical stability
    #   device: torch.device | None = None
    #   dtype: torch.dtype | None = None

def forward(self, x: torch.Tensor) -> torch.Tensor
    # Process an input tensor of shape (batch_size, sequence_length, d_model) and return a tensor of the same shape
```

**Mathematical Definition:**

For a vector `a ∈ R^d_model` of activations, RMSNorm rescales each activation `a_i` as follows:

```
RMSNorm(a_i) = (a_i / RMS(a)) * g_i
```

where `RMS(a) = sqrt((1/d_model) * sum(a_i²) + ε)` and `g_i` is a learnable "gain" parameter.

**Requirements:**

- Upcast input to `torch.float32` before performing normalization, then downcast to original dtype
- Initialize gain parameters to 1
- Process tensors of shape `(batch_size, sequence_length, d_model)`

To test your implementation, implement the test adapter at `adapters.run_rmsnorm`, then run `uv run pytest -k test_rmsnorm`.

### Problem 3.4: Implement the Position-Wise Feed-Forward Network (2 points)

**Deliverable:** Implement the SwiGLU feed-forward network, composed of a SiLU activation function and a GLU.

**Mathematical Definition:**

```
FFN(x) = SwiGLU(x, W1, W2, W3) = W2(SiLU(W1x) ⊙ W3x)
```

where:

- `SiLU(x) = x · σ(x) = x / (1 + e^(-x))`
- `⊙` represents element-wise multiplication
- `x ∈ R^d_model`, `W1, W3 ∈ R^(d_ff × d_model)`, `W2 ∈ R^(d_model × d_ff)`
- Canonically, `d_ff = (8/3) × d_model`

**Requirements:**

- Set `d_ff` to approximately `(8/3) × d_model`, while ensuring the dimensionality is a multiple of 64
- You may use `torch.sigmoid` for numerical stability
- No bias terms

To test your implementation, implement the test adapter at `adapters.run_swiglu`, then run `uv run pytest -k test_swiglu`.

### Problem 3.5: Implement RoPE (2 points)

**Deliverable:** Implement a class `RotaryPositionalEmbedding` that applies RoPE (Rotary Position Embeddings) to the input tensor.

**Recommended interface:**

```python
def __init__(self, theta: float, d_k: int, max_seq_len: int, device=None)
    # Construct the RoPE module and create buffers if needed
    # Parameters:
    #   theta: float - Θ value for the RoPE
    #   d_k: int - dimension of query and key vectors
    #   max_seq_len: int - Maximum sequence length that will be inputted
    #   device: torch.device | None = None

def forward(self, x: torch.Tensor, token_positions: torch.Tensor) -> torch.Tensor
    # Process an input tensor of shape (..., seq_len, d_k) and return a tensor of the same shape
    # Parameters:
    #   x: tensor of shape (..., seq_len, d_k)
    #   token_positions: tensor of shape (..., seq_len) specifying token positions
```

**Mathematical Definition:**

For a query token `q^(i) = W_q * x^(i) ∈ R^d` at token position `i`, apply a pairwise rotation matrix `R_i`, giving `q'^(i) = R_i * q^(i)`. The rotation matrix `R_i` rotates pairs of embedding elements as 2D vectors by angle `θ_{i,k} = Θ * (2^(k-1)) / d` for `k ∈ {1, ..., d/2}`.

**Requirements:**

- Tolerate `x` with an arbitrary number of batch dimensions
- Use token positions to slice precomputed cos and sin tensors along the sequence dimension
- You may pre-compute sin and cos values in `__init__` using `self.register_buffer(persistent=False)`
- This layer has no learnable parameters

To test your implementation, complete `adapters.run_rope` and make sure it passes `uv run pytest -k test_rope`.

### Problem 3.6: Implement Softmax (1 point)

**Deliverable:** Write a function to apply the softmax operation on a tensor. Your function should take two parameters: a tensor and a dimension `i`, and apply softmax to the `i`-th dimension of the input tensor.

**Mathematical Definition:**

```
softmax(v)_i = exp(v_i) / sum_j(exp(v_j))
```

**Requirements:**

- Use the trick of subtracting the maximum value in the `i`-th dimension from all elements to avoid numerical stability issues
- The output tensor should have the same shape as the input tensor, but its `i`-th dimension will now have a normalized probability distribution

To test your implementation, complete `adapters.run_softmax` and make sure it passes `uv run pytest -k test_softmax_matches_pytorch`.

### Problem 3.7: Implement Scaled Dot-Product Attention (5 points)

**Deliverable:** Implement the scaled dot-product attention function.

**Mathematical Definition:**

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V
```

where `Q ∈ R^(n×d_k)`, `K ∈ R^(m×d_k)`, and `V ∈ R^(m×d_v)`.

**Requirements:**

- Handle keys and queries of shape `(batch_size, ..., seq_len, d_k)` and values of shape `(batch_size, ..., seq_len, d_v)`, where `...` represents any number of other batch-like dimensions
- Return an output with shape `(batch_size, ..., d_v)`
- Support an optional user-provided boolean mask of shape `(seq_len, seq_len)`
- The attention probabilities of positions with a mask value of `True` should collectively sum to 1
- The attention probabilities of positions with a mask value of `False` should be zero
- For masking, add `-∞` to pre-softmax values where mask is `False`

To test your implementation, implement the test adapter at `adapters.run_scaled_dot_product_attention`. Run `uv run pytest -k test_scaled_dot_product_attention` for third-order tensors and `uv run pytest -k test_4d_scaled_dot_product_attention` for fourth-order tensors.

### Problem 3.8: Implement Causal Multi-Head Self-Attention (5 points)

**Deliverable:** Implement causal multi-head self-attention as a `torch.nn.Module`.

**Mathematical Definition:**

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h)
head_i = Attention(Q_i, K_i, V_i)
MultiHeadSelfAttention(x) = W_O * MultiHead(W_Q*x, W_K*x, W_V*x)
```

**Recommended interface:**

```python
def __init__(self, d_model: int, num_heads: int, ...)
    # Parameters:
    #   d_model: int - Dimensionality of the Transformer block inputs
    #   num_heads: int - Number of heads to use in multi-head self-attention
```

**Requirements:**

- Set `d_k = d_v = d_model / num_heads`
- Implement causal masking: token `i` can only attend to positions `j ≤ i`
- Apply RoPE to query and key vectors, but not value vectors
- Handle head dimension as a batch dimension (same RoPE rotation for each head)
- Compute key, query, and value projections (three matrix multiplies total)

To test your implementation, implement the test adapter at `adapters.run_multihead_self_attention`, then run `uv run pytest -k test_multihead_self_attention`.

### Problem 3.9: Implement the Transformer Block (3 points)

**Deliverable:** Implement the pre-norm Transformer block as described and illustrated in the assignment.

**Recommended interface:**

```python
def __init__(self, d_model: int, num_heads: int, d_ff: int, ...)
    # Parameters:
    #   d_model: int - Dimensionality of the Transformer block inputs
    #   num_heads: int - Number of heads to use in multi-head self-attention
    #   d_ff: int - Dimensionality of the position-wise feed-forward inner layer
```

**Architecture:**

A Transformer block contains two sub-layers:

1. Multi-head self-attention sublayer: `y = x + MultiHeadSelfAttention(RMSNorm(x))`
2. Position-wise feed-forward sublayer: `z = y + FFN(RMSNorm(y))`

To test your implementation, implement the adapter `adapters.run_transformer_block`, then run `uv run pytest -k test_transformer_block`.

### Problem 3.10: Implementing the Transformer LM (3 points)

**Deliverable:** Implement the Transformer language model as described in the assignment.

**Recommended interface:**

```python
def __init__(self, vocab_size: int, context_length: int, num_layers: int,
             d_model: int, num_heads: int, d_ff: int, ...)
    # Parameters:
    #   vocab_size: int - The size of the vocabulary
    #   context_length: int - The maximum context length
    #   num_layers: int - The number of Transformer blocks to use
    #   d_model: int - Hidden dimension
    #   num_heads: int - Number of attention heads
    #   d_ff: int - Feed-forward dimension
```

**Architecture:**

1. Token embedding layer: converts token IDs to dense vectors
2. `num_layers` Transformer blocks
3. Final RMSNorm
4. Output embedding (LM head): linear transformation to produce logits over vocabulary

To test your implementation, implement the test adapter at `adapters.run_transformer_lm`, then run `uv run pytest -k test_transformer_lm`.

### Problem 3.11: Transformer LM Resource Accounting (5 points)

(a) Consider GPT-2 XL, which has the following configuration:

- `vocab_size`: 50,257
- `context_length`: 1,024
- `num_layers`: 48
- `d_model`: 1,600
- `num_heads`: 25
- `d_ff`: 6,400

Suppose we constructed our model using this configuration. How many trainable parameters would our model have? Assuming each parameter is represented using single-precision floating point, how much memory is required to just load this model?  
Deliverable: A one-to-two sentence response.

(b) Identify the matrix multiplies required to complete a forward pass of our GPT-2 XL-shaped model. How many FLOPs do these matrix multiplies require in total? Assume that our input sequence has `context_length` tokens.  
Deliverable: A list of matrix multiplies (with descriptions), and the total number of FLOPs required.

(c) Based on your analysis above, which parts of the model require the most FLOPs?  
Deliverable: A one-to-two sentence response.

(d) Repeat your analysis with GPT-2 small (12 layers, 768 d_model, 12 heads), GPT-2 medium (24 layers, 1024 d_model, 16 heads), and GPT-2 large (36 layers, 1280 d_model, 20 heads). As the model size increases, which parts of the Transformer LM take up proportionally more or less of the total FLOPs?  
Deliverable: For each model, provide a breakdown of model components and its associated FLOPs (as a proportion of the total FLOPs required for a forward pass). In addition, provide a one-to-two sentence description of how varying the model size changes the proportional FLOPs of each component.

(e) Take GPT-2 XL and increase the context length to 16,384. How does the total FLOPs for one forward pass change? How do the relative contribution of FLOPs of the model components change?  
Deliverable: A one-to-two sentence response.

---

## Part 4: Training a Transformer LM

### Background

We now have the steps to preprocess the data (via tokenizer) and the model (Transformer). What remains is to build all of the code to support training:

- Loss: we need to define the loss function (cross-entropy)
- Optimizer: we need to define the optimizer to minimize this loss (AdamW)
- Training loop: we need all the supporting infrastructure that loads data, saves checkpoints, and manages training

### Problem 4.1: Implement Cross Entropy (1 point)

**Deliverable:** Write a function to compute the cross entropy loss, which takes in predicted logits `(o_i)` and targets `(x_{i+1})` and computes the cross entropy `ℓ_i = -log softmax(o_i)[x_{i+1}]`.

**Requirements:**

- Subtract the largest element for numerical stability
- Cancel out log and exp whenever possible
- Handle any additional batch dimensions and return the average across the batch
- Batch-like dimensions always come first, before the vocabulary size dimension

Implement `adapters.run_cross_entropy`, then run `uv run pytest -k test_cross_entropy`.

**Note:** For evaluation, you may also want to compute perplexity:

```
perplexity = exp((1/m) * sum(ℓ_i))
```

### Problem 4.2: Tuning the Learning Rate (1 point)

Run the SGD example from the assignment with three other values for the learning rate: `1e1`, `1e2`, and `1e3`, for just 10 training iterations. What happens with the loss for each of these learning rates? Does it decay faster, slower, or does it diverge (i.e., increase over the course of training)?  
Deliverable: A one-to-two sentence response with the behaviors you observed.

### Problem 4.3: Implement AdamW (2 points)

**Deliverable:** Implement the AdamW optimizer as a subclass of `torch.optim.Optimizer`.

**Algorithm:**

```
Initialize: m ← 0, v ← 0
For t = 1, ..., T:
    Sample batch B_t
    g ← ∇_θ ℓ(θ; B_t)
    m ← β_1*m + (1 - β_1)*g
    v ← β_2*v + (1 - β_2)*g²
    α_t ← α * sqrt(1 - β_2^t) / (1 - β_1^t)
    θ ← θ - α_t * m / (sqrt(v) + ε)
    θ ← θ - α*λ*θ  (weight decay)
```

**Requirements:**

- Your class should take the learning rate `α` in `__init__`, as well as the `β1`, `β2`, `ε`, and `λ` hyperparameters
- Use `self.state` to keep track of moment estimates for each parameter
- Note that `t` starts at 1

Implement `adapters.get_adamw_cls` and make sure it passes `uv run pytest -k test_adamw`.

### Problem 4.4: Resource Accounting for Training with AdamW (2 points)

Let us compute how much memory and compute running AdamW requires. Assume we are using `float32` for every tensor.

(a) How much peak memory does running AdamW require? Decompose your answer based on the memory usage of the parameters, activations, gradients, and optimizer state. Express your answer in terms of the `batch_size` and the model hyperparameters (`vocab_size`, `context_length`, `num_layers`, `d_model`, `num_heads`). Assume `d_ff = 4 × d_model`.  
Deliverable: An algebraic expression for each of parameters, activations, gradients, and optimizer state, as well as the total.

(b) Instantiate your answer for a GPT-2 XL-shaped model to get an expression that only depends on the `batch_size`. What is the maximum batch size you can use and still fit within 80GB memory?  
Deliverable: An expression that looks like `a · batch_size + b` for numerical values `a`, `b`, and a number representing the maximum batch size.

(c) How many FLOPs does running one step of AdamW take?  
Deliverable: An algebraic expression, with a brief justification.

(d) Model FLOPs utilization (MFU) is defined as the ratio of observed throughput (tokens per second) relative to the hardware's theoretical peak FLOP throughput. An NVIDIA A100 GPU has a theoretical peak of 19.5 teraFLOP/s for float32 operations. Assuming you are able to get 50% MFU, how long would it take to train a GPT-2 XL for 400K steps and a batch size of 1024 on a single A100? Following Kaplan et al. [2020] and Hoffmann et al. [2022], assume that the backward pass has twice the FLOPs of the forward pass.  
Deliverable: The number of days training would take, with a brief justification.

### Problem 4.5: Implement Cosine Learning Rate Schedule with Warmup (1 point)

**Deliverable:** Write a function that takes `t`, `α_max`, `α_min`, `T_w` and `T_c`, and returns the learning rate `α_t` according to the scheduler defined below.

**Schedule Definition:**

- (Warm-up) If `t < T_w`, then `α_t = (t / T_w) * α_max`
- (Cosine annealing) If `T_w ≤ t ≤ T_c`, then `α_t = α_min + (1/2) * (1 + cos((t - T_w) / (T_c - T_w) * π)) * (α_max - α_min)`
- (Post-annealing) If `t > T_c`, then `α_t = α_min`

Implement `adapters.get_lr_cosine_schedule` and make sure it passes `uv run pytest -k test_get_lr_cosine_schedule`.

### Problem 4.6: Implement Gradient Clipping (1 point)

**Deliverable:** Write a function that implements gradient clipping. Your function should take a list of parameters and a maximum `ℓ2`-norm. It should modify each parameter gradient in place.

**Algorithm:**

Given the gradient `g` (for all parameters), compute its `ℓ2`-norm `||g||_2`. If this norm is less than a maximum value `M`, then leave `g` as is; otherwise, scale `g` down by a factor of `M / (||g||_2 + ε)` (where `ε = 10^-6` for numeric stability).

Implement the adapter `adapters.run_gradient_clipping` and make sure it passes `uv run pytest -k test_gradient_clipping`.

---

## Part 5: Training Loop

### Problem 5.1: Implement Data Loading (2 points)

**Deliverable:** Write a function that takes a numpy array `x` (integer array with token IDs), a `batch_size`, a `context_length` and a PyTorch device string (e.g., `'cpu'` or `'cuda:0'`), and returns a pair of tensors: the sampled input sequences and the corresponding next-token targets. Both tensors should have shape `(batch_size, context_length)` containing token IDs, and both should be placed on the requested device.

**Note:** For large datasets that don't fit in memory, use `np.memmap` or `np.load` with `mmap_mode='r'` to load data in memory-mapped mode.

To test your implementation, implement the test adapter at `adapters.run_get_batch`, then run `uv run pytest -k test_get_batch`.

### Problem 5.2: Implement Model Checkpointing (1 point)

**Deliverable:** Implement the following two functions to load and save checkpoints:

```python
def save_checkpoint(model, optimizer, iteration, out)
    # Dump all the state from the first three parameters into the file-like object out
    # Parameters:
    #   model: torch.nn.Module
    #   optimizer: torch.optim.Optimizer
    #   iteration: int
    #   out: str | os.PathLike | typing.BinaryIO | typing.IO[bytes]

def load_checkpoint(src, model, optimizer)
    # Load a checkpoint from src and recover the model and optimizer states
    # Returns: the iteration number that was saved to the checkpoint
    # Parameters:
    #   src: str | os.PathLike | typing.BinaryIO | typing.IO[bytes]
    #   model: torch.nn.Module
    #   optimizer: torch.optim.Optimizer
```

**Requirements:**

- Use `state_dict()` method of both model and optimizer to get their states
- Use `torch.save(obj, out)` to save and `torch.load(src)` to load
- Use `load_state_dict()` to restore states

Implement the adapters `adapters.run_save_checkpoint` and `adapters.run_load_checkpoint`, and make sure they pass `uv run pytest -k test_checkpointing`.

### Problem 5.3: Put It Together (4 points)

**Deliverable:** Write a script that runs a training loop to train your model on user-provided input. In particular, your training script should allow for (at least) the following:

- Ability to configure and control the various model and optimizer hyperparameters
- Memory-efficient loading of training and validation large datasets with `np.memmap`
- Serializing checkpoints to a user-provided path
- Periodically logging training and validation performance (e.g., to console and/or an external service like Weights and Biases)

---

## Part 6: Generating Text

### Problem 6.1: Decoding (3 points)

**Deliverable:** Implement a function to decode from your language model. We recommend that you support the following features:

- Generate completions for a user-provided prompt (i.e., take some `x_{1...t}` and sample a completion until you hit an `<|endoftext|>` token)
- Allow the user to control the maximum number of generated tokens
- Given a desired temperature value, apply softmax temperature scaling to the predicted next-word distributions before sampling
- Top-p sampling (nucleus sampling), given a user-specified threshold value

**Temperature Scaling:**

```
softmax(v, τ)_i = exp(v_i / τ) / sum_j(exp(v_j / τ))
```

**Top-p (Nucleus) Sampling:**

Given a probability distribution `q` from a temperature-scaled softmax, nucleus sampling with hyperparameter `p` produces the next token according to:

```
P(x_{t+1} = i | q) = {
    q_i / sum_{j ∈ V(p)} q_j  if i ∈ V(p)
    0                         otherwise
}
```

where `V(p)` is the smallest set of indices such that `sum_{j ∈ V(p)} q_j ≥ p`.

---

## Part 7: Experiments

### Problem 7.1: Experiment Logging (3 points)

For your training and evaluation code, create experiment tracking infrastructure that allows you to track your experiments and loss curves with respect to gradient steps and wallclock time.  
Deliverable: Logging infrastructure code for your experiments and an experiment log (a document of all the things you tried) for the assignment problems below in this section.

### Problem 7.2: Tune the Learning Rate (3 points)

The learning rate is one of the most important hyperparameters to tune. Taking the base model you've trained, answer the following questions:

(a) Perform a hyperparameter sweep over the learning rates and report the final losses (or note divergence if the optimizer diverges).  
Deliverable: Learning curves associated with multiple learning rates. Explain your hyperparameter search strategy.  
Deliverable: A model with validation loss (per-token) on TinyStories of at most 1.45

(b) Folk wisdom is that the best learning rate is "at the edge of stability." Investigate how the point at which learning rates diverge is related to your best learning rate.  
Deliverable: Learning curves of increasing learning rate which include at least one divergent run and an analysis of how this relates to convergence rates.

**Base Hyperparameters for TinyStories:**

- `vocab_size`: 10000
- `context_length`: 256
- `d_model`: 512
- `d_ff`: 1344 (roughly `8/3 * d_model`, multiple of 64)
- RoPE theta parameter `Θ`: 10000
- Number of layers and heads: 4 layers, 16 heads (about 17M non-embedding parameters)
- Total tokens processed: 327,680,000 (`batch_size × total_step_count × context_length`)

You should do some trial and error to find good defaults for: learning rate, learning rate warmup, other AdamW hyperparameters (`β1`, `β2`, `ε`), and weight decay.

### Problem 7.3: Batch Size Variations (1 point)

Vary your batch size all the way from 1 to the GPU memory limit. Try at least a few batch sizes in between, including typical sizes like 64 and 128.  
Deliverable: Learning curves for runs with different batch sizes. The learning rates should be optimized again if necessary.  
Deliverable: A few sentences discussing your findings on batch sizes and their impacts on training.

### Problem 7.4: Generate Text (1 point)

Using your decoder and your trained checkpoint, report the text generated by your model. You may need to manipulate decoder parameters (temperature, top-p, etc.) to get fluent outputs.  
Deliverable: Text dump of at least 256 tokens of text (or until the first `<|endoftext|>` token), and a brief comment on the fluency of this output and at least two factors which affect how good or bad this output is.

### Problem 7.5: Remove RMSNorm and Train (1 point)

Remove all of the RMSNorms from your Transformer and train. What happens at the previous optimal learning rate? Can you get stability by using a lower learning rate?  
Deliverable: A learning curve for when you remove RMSNorms and train, as well as a learning curve for the best learning rate.  
Deliverable: A few sentence commentary on the impact of RMSNorm.

### Problem 7.6: Implement Post-Norm and Train (1 point)

Modify your pre-norm Transformer implementation into a post-norm one. Train with the post-norm model and see what happens.  
Deliverable: A learning curve for a post-norm transformer, compared to the pre-norm one.

**Post-norm Architecture:**

```
z = RMSNorm(x + MultiHeadedSelfAttention(x))
y = RMSNorm(z + FFN(z))
```

### Problem 7.7: Implement NoPE (1 point)

Modify your Transformer implementation with RoPE to remove the position embedding information entirely, and see what happens.  
Deliverable: A learning curve comparing the performance of RoPE and NoPE.

### Problem 7.8: SwiGLU vs. SiLU (1 point)

Test the importance of gating in the feed-forward network by comparing the performance of SwiGLU feed-forward networks versus feed-forward networks using SiLU activations but no gated linear unit (GLU):

```
FFN_SiLU(x) = W2 * SiLU(W1 * x)
```

In your `FFN_SiLU` implementation, set `d_ff = 4 × d_model` to approximately match the parameter count of the SwiGLU feed-forward network (which has three instead of two weight matrices).  
Deliverable: A learning curve comparing the performance of SwiGLU and SiLU feed-forward networks, with approximately matched parameter counts.  
Deliverable: A few sentences discussing your findings.

### Problem 7.9: Experiment on OpenWebText (2 points)

Train your language model on OpenWebText with the same model architecture and total training iterations as TinyStories. How well does this model do?  
Deliverable: A learning curve of your language model on OpenWebText. Describe the difference in losses from TinyStories – how should we interpret these losses?  
Deliverable: Generated text from OpenWebText LM, in the same format as the TinyStories outputs. How is the fluency of this text? Why is the output quality worse even though we have the same model and compute budget as TinyStories?

**Note:** You may have to re-tune your hyperparameters such as learning rate or batch size for this experiment.

### Problem 7.10: Leaderboard (6 points)

You will train a model under the leaderboard rules with the goal of minimizing the validation loss of your language model within 1.5 H100-hour.

**Rules for the leaderboard:**

- Runtime: Your submission can run for at most 1.5 hours on an H100
- Data: You may only use the OpenWebText training dataset that we provide
- Otherwise, you are free to do whatever your heart desires

**Deliverable:** The final validation loss that was recorded, an associated learning curve that clearly shows a wallclock-time x-axis that is less than 1.5 hours and a description of what you did. We expect a leaderboard submission to beat at least the naive baseline of a 5.0 loss.

Submit to the leaderboard at: https://github.com/stanford-cs336/assignment1-basics-leaderboard

---

## Additional Notes

### Datasets

This assignment uses two pre-processed datasets:

- **TinyStories**: A simple dataset for quick training and experimentation
- **OpenWebText**: A more standard pretraining dataset created from a webcrawl

Both datasets are single, large plaintext files. Instructions for accessing these datasets are provided in the assignment repository.

### Testing

To test your implementations, you will need to:

1. Implement the corresponding adapter functions in `adapters.py`
2. Run the appropriate pytest commands (e.g., `uv run pytest -k test_name`)

The adapters serve as glue code that connects your implementations to the test suite. Your changes to `adapters.py` should not contain any substantive logic.

### Einsum Notation

We strongly recommend using einsum notation (via `einops` or `einx`) for tensor operations throughout the assignment. This makes your code more readable and self-documenting, and helps with handling arbitrary batch dimensions.
