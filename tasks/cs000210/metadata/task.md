# Understanding LLM / Transformers

## Prerequisites

### Environment Setup

1. **GPU Check**: Verify GPU availability using `nvidia-smi`

2. **Install Dependencies**: 
   - Install `transformers==4.47.0` (do not alter the version for stable usage)
   - Install `sae-lens` for Q7

3. **Huggingface Login**:
   - Create a Huggingface token (hf_token)
   - Login to Huggingface using the token to access the Gemma model
   - Accept the license for the Gemma model at: https://huggingface.co/google/gemma-2-2b-it

### Model Setup

- **Model**: `google/gemma-2-2b-it` from Huggingface
- **Model URL**: https://huggingface.co/google/gemma-2-2b-it
- Load the model with `torch.float16` dtype and `device_map="cuda"`

### Evaluation Model

- **Scoring Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2` from Huggingface
- **Model URL**: https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2
- Used for calculating coherence scores between questions and answers

## Q1: Chat Template Comparison

### Objective
Observe whether the chat template affects the model's output results by comparing responses generated with and without chat templates.

### Tasks

1. **Q1.1 ~ Q1.4**: Implement the `generate_text_from_prompt` function
   - Function signature: `generate_text_from_prompt(prompt, tokenizer, model)`
   - Parameters:
     - `prompt` (str): the prompt inputted to the model
     - `tokenizer`: the tokenizer used to encode/decode input/output
     - `model`: the model used to generate output
   - Returns: the response of the model
   - Requirements:
     - Use `do_sample=False` to get a deterministic response
     - Otherwise the coherence score may be different from the sample answer
   - Reference: https://huggingface.co/google/gemma-2-2b-it

2. **Comparison**:
   - Generate responses with chat template using `tokenizer.apply_chat_template()`
   - Generate responses without chat template (directly using plain text)
   - Calculate coherence scores for both responses using the provided `calculate_coherence` function
   - Compare the coherence scores

## Q2: Multi-turn Conversations

### Objective
Implement a multi-turn conversation system and observe the chat template format and token probability distributions.

### Tasks

1. **Q2.1 ~ Q2.3**: Observe the prompt with chat template format
   - Print the prompt with chat template format that is inputted to the model in each round
   - Analyze how the chat history is formatted across multiple conversation rounds

2. **Token Probability Visualization**:
   - Extract logits from model outputs
   - Apply softmax to get probabilities
   - Visualize top-k token probabilities for the next word using bar plots
   - Generate responses using the model with `max_new_tokens=200` and `do_sample=False`

## Q3: Tokenization of Sentence

### Objective
Understand how tokenization works by encoding sentences into token IDs and converting them back to tokens.

### Tasks

1. **Q3.1 ~ Q3.4**: Implement tokenization
   - Encode a sentence into token IDs without adding special tokens
   - Convert the token IDs back to their corresponding tokens (words or subwords)
   - Print each token and its corresponding token index (ID)
   - Reference: 
     - https://huggingface.co/learn/nlp-course/en/chapter2/4?fw=pt
     - https://huggingface.co/docs/transformers/en/main_classes/tokenizer

### Test Sentence
```
"I love taking a Machine Learning course by Professor Hung-yi Lee, What about you?"
```

## Q4: Auto-regressive Generation

### Objective
Implement and compare top-k sampling and nucleus (top-p) sampling methods for text generation.

### Tasks

1. **Q4.3 ~ Q4.6**: Implement text generation with sampling methods
   - Modify the values of `k` (for top-k sampling) and `p` (for nucleus sampling) accordingly
   - Implement top-p sampling generation (top-k sampling is already provided as reference)
   - Generate 20 sentences for each method using the same prompt
   - Reference: https://huggingface.co/docs/transformers/en/main_classes/text_generation

2. **Evaluation**:
   - Calculate self-BLEU scores for both top-k and top-p generated sentences
   - Compare the diversity of generated texts between the two methods

### Generation Parameters
- `max_generation_tokens = 30`
- `do_sample = True` (enable sampling)
- `use_cache = True` (enable KV cache)
- `return_dict_in_generate = True`

### Prompt
```
"Generate a paraphrase of the sentence 'Professor Hung-yi Lee is one of the best teachers in the domain of machine learning'. Just response with one sentence."
```

## Q5: t-SNE Visualization

### Objective
Visualize word embeddings using t-SNE to observe how words with different meanings are represented in the embedding space.

### Tasks

1. **Q5.2 ~ Q5.3**: Analyze word embeddings
   - Use sentences containing words with different meanings (e.g., "Apple" as fruit vs. company)
   - Extract hidden states from the last layer of the model
   - Compute sentence-level embeddings using mean pooling
   - Apply t-SNE to reduce embeddings to 2D
   - Visualize the embeddings and observe how words with different meanings cluster

### Test Sentences
- "I ate a fresh apple." (Apple - fruit)
- "Apple released the new iPhone." (Apple - company)
- "I peeled an orange and ate it." (Orange - fruit)
- "The Orange network has great coverage." (Orange - telecom)
- "Microsoft announced a new update." (Microsoft - company)
- "Banana is my favorite fruit." (Banana - fruit)

### Parameters
- `n_components = 2`
- `perplexity = 2`
- `random_state = 42`

## Q6: Observe the Attention Weight

### Objective
Extract and visualize attention weights during text generation to understand what the model focuses on.

### Tasks

1. **Q6.1 ~ Q6.4**: Extract attention information
   - Get the logits for the last generated token from model outputs
   - Extract the attention scores from the model's outputs
   - Reference: https://huggingface.co/docs/transformers/en/main_classes/output#transformers.modeling_outputs.BaseModelOutput.attentions

2. **Visualization**:
   - Extract attention weights for a specified layer and head
   - Collect attention weights across multiple generation steps
   - Visualize attention weights as a heatmap showing which tokens attend to which tokens

### Parameters
- `generation_tokens = 20`
- `layer_idx = 10` (layer index for attention visualization)
- `head_idx = 7` (attention head index to visualize)
- `prompt = "Google "`

### Requirements
- Use KV cache (`HybridCache`) for efficient generation
- Set `output_attentions=True` when calling the model
- Generate tokens one by one to collect attention weights at each step

## Q7: Observe the Activation Scores

### Objective
Analyze model activations using Sparse Autoencoders (SAE) to understand internal representations.

### Prerequisites
- Install `sae-lens` package
- Load SAE model: `gemma-scope-2b-pt-res-canonical` with `sae_id = "layer_20/width_16k/canonical"`
- Reference tutorials:
  - [Gemma Tutorial From Scratch](https://colab.research.google.com/drive/17dQFYUYnuKnP6OwQPH9v_GSYUW5aj-Rp#scrollTo=2-i7YRVLgKoT)
  - [SAELens](https://github.com/jbloomAus/SAELens/blob/main/tutorials/tutorial_2_0.ipynb)

### Q7.1: Feature Dashboard

**Task**: Explore a specific feature using the Neuronpedia dashboard
- Use feature index `10004`
- Generate dashboard HTML using the provided `get_dashboard_html` function
- Observe the feature's behavior and characteristics

### Q7.2 ~ Q7.3: Maximum Activations Comparison

**Objective**: Compare maximum activations for different prompts

**Tasks**:
- Implement or use the provided `get_max_activation` function
- Calculate maximum activation for feature index `10004` for two different prompts:
  - Prompt A: "Time travel offers me the opportunity to correct past errors, but it comes with its own set of risks."
  - Prompt B: "I accept that my decisions shape my future, and though mistakes are inevitable, they define who I become."
- Plot activation distribution histograms for each prompt
- Compare the maximum activation values

### Q7.4 ~ Q7.6: Activation Distribution for Specific Layer

**Objective**: Analyze activation distribution across tokens in a specific layer

**Tasks**:
- Use the provided `plot_token_activations` function
- Analyze activations for layer 24
- Observe how different tokens activate the specified feature (feature index 10004)
- Visualize token-wise activations using bar plots

**Test Prompt**:
```
"Time travel will become a reality as technology continues to advance."
```

**Parameters**:
- `layer_idx = 24`
- `feature_idx = 10004`

### Q7.7 ~ Q7.9: Activation Distribution for Specific Token

**Objective**: Analyze how a specific token's activation changes across all layers

**Tasks**:
- Use the provided `plot_layer_activations` function
- Alter the token index to observe different tokens
- Visualize how activation values change across all model layers for a specific token
- Analyze the activation pattern

**Test Prompt**:
```
"Time travel will become a reality as technology continues to advance."
```

**Parameters**:
- `token_idx = 1` (can be modified to observe different tokens)
- `feature_idx = 10004`

## General Notes

- All code should be implemented in the provided notebook structure
- Use deterministic generation (`do_sample=False`) where specified to ensure reproducible results
- Ensure proper GPU usage by moving tensors to CUDA device
- Use `torch.no_grad()` context for inference to save memory
- Follow the TODO markers in the notebook to identify which parts need implementation
- Reference documentation links are provided for each task - use them to understand the APIs and expected behavior

