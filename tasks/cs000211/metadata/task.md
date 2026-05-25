# Homework 5: Finetuning is Powerful

## Overview

This assignment focuses on fine-tuning a large language model using LoRA (Low-Rank Adaptation) techniques. You will work with the Unsloth framework to efficiently fine-tune a pre-trained model on a conversational dataset.

## Important Constraints

- **Model Restriction**: You must use the model `unsloth/Llama-2-7b-bnb-4bit`. Changing the model or quantization version is strictly forbidden.
- **Training Data Limit**: You are limited to using exactly 100 samples from the sorted dataset for training. No more than 100 data points are allowed.
- **Seed**: The random seed (3407) must not be modified to ensure reproducibility.

## Setup

### Environment Setup

Install the required packages:
- bitsandbytes, accelerate, xformers==0.0.29, peft, trl, triton
- cut_cross_entropy
- sentencepiece, protobuf, datasets, huggingface_hub, hf_transfer
- unsloth==2025.2.15, unsloth_zoo==2025.2.7
- transformers==4.49.0

### Dataset

The dataset is located at `/content/ML_Spring2025_HW5/fastchat_alpaca_52k` and contains:
- `id`: Unique identifier for each example
- `conversations`: List of conversation messages with roles ("user", "assistant")
- `score`: Quality score for each example
- `text`: Text field (to be added during preprocessing)

The test set is located at `/content/ML_Spring2025_HW5/test_set_evol_instruct_150.json`.

## Tasks

### Task 1: Model Initialization

Initialize the model with the following requirements:
- Model: `unsloth/Llama-2-7b-bnb-4bit` (do not change)
- `max_seq_length`: 2048
- `dtype`: None (auto detection)
- `load_in_4bit`: True

Use the llama-3.1 chat template for tokenization.

### Task 2: LoRA Adapter Configuration

Configure LoRA adapters with the following considerations:
- `r`: Choose any number > 0. Common values are 4, 8, 16, 32, 64, 128. Higher ranks allow more expressive power but also increase parameter count.
- `lora_alpha`: Choose any number > 0. Suggested values are 4, 8, 16, 32, 64, 128.
- `target_modules`: `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]`
- `lora_dropout`: Supports any value, but 0 is optimized
- `bias`: Supports any value, but "none" is optimized
- `use_gradient_checkpointing`: "unsloth" (for very long context)
- `random_state`: 3407 (do not modify)
- `use_rslora`: False (rank stabilized LoRA is supported)
- `loftq_config`: None (LoftQ is supported)

### Task 3: Data Preprocessing and Sorting

#### 3.1 Conversation Length Computation

Implement a helper function `compute_conversation_length(example)` that computes the conversation length. The default "conversation length" refers to the length of the input (human) and output (assistant). You may modify this definition as needed.

#### 3.2 Simple Sorting

Sort the dataset from shortest to longest conversation (by word count) in ascending order.

#### 3.3 Advanced Sorting

Implement an `advanced_sort_key(example)` function that combines conversation length with the 'score' field. The default implementation uses a weighted sum, but you may modify the sorting strategy.

#### 3.4 Dataset Selection

Select which sorted dataset to use for training (`sorted_dataset_simple` or `sorted_dataset_advanced`). You can select any 100 consecutive samples from the sorted dataset (e.g., `range(0,100)` or `range(50,150)`).

### Task 4: Training Configuration

Configure the training hyperparameters. The following parameters need to be tuned:
- `per_device_train_batch_size`: Batch size per device
- `gradient_accumulation_steps`: Number of gradient accumulation steps
- `warmup_steps`: Number of warmup steps
- `num_train_epochs`: Number of training epochs
- `learning_rate`: Learning rate
- `optim`: Optimizer (e.g., "adamw_8bit")
- `weight_decay`: Weight decay coefficient
- `lr_scheduler_type`: Learning rate scheduler type (e.g., "linear")
- `seed`: 3407 (do not modify)

The training uses:
- `SFTTrainer` from the `trl` library
- `DataCollatorForSeq2Seq` for data collation
- `train_on_responses_only` to only train on assistant outputs (ignoring loss on user inputs)
- Automatic precision selection (fp16 for Tesla T4/V100, bf16 for Ampere+)

### Task 5: Curriculum Training (Optional)

Implement curriculum training by starting with "easier" examples (e.g., shorter, clearer conversations) and progressively introducing more complex ones. The total amount of data used for training should still not exceed 100 samples.

Example approach:
- Step 1: Train on `sorted_dataset_simple`
- Step 2: Train on `sorted_dataset_advanced`

### Task 6: Inference Configuration

Configure the decoding parameters for generation:
- `do_sample`: Whether to use sampling
- `max_new_tokens`: Maximum number of new tokens to generate
- `use_cache`: Whether to use cache
- `temperature`: Sampling temperature
- `top_p`: Nucleus sampling parameter
- `top_k`: Top-k sampling parameter

Generate predictions for the test set and save the results to `pred.json` with the following format:
```json
{
  "entry_id": {
    "input": [messages],
    "output": [parsed_outputs]
  }
}
```

The `parse_true_output` function extracts the assistant response from the decoded output by:
1. Finding the assistant header token: `<|start_header_id|>assistant<|end_header_id|>\n\n`
2. Extracting everything after it until the first occurrence of `<|eot_id|>`
3. If the assistant header is not found, falling back to the last occurrence of `<|end_header_id|>\n\n`

Also save the training configuration to `training_config.json`.

## Notes

- The llama-3.1 chat template adds metadata like "Cutting Knowledge Date: December 2023\nToday Date: 26 July 2024" by default. This is expected behavior.
- Unsloth enables faster training and inference through optimized implementations.
- The dataset contains 52,002 examples, but you can only use 100 for training.
- The test set contains 150 examples.

## Deliverables

1. Fine-tuned model (LoRA adapters)
2. `pred.json`: Inference results on the test set
3. `training_config.json`: Training hyperparameters used

## References

- Unsloth: https://github.com/unslothai/unsloth
- Hugging Face Transformers: https://huggingface.co/docs/transformers
- TRL (Transformer Reinforcement Learning): https://github.com/huggingface/trl

