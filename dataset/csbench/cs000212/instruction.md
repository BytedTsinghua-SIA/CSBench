# ML2025 Homework 6 - Fine-tuning leads to Forgetting

## Task Overview

This homework focuses on the problem of fine-tuning leading to forgetting. You will fine-tune a language model using the GSM8K dataset and observe the effects on previously learned knowledge. The goal is to implement and optimize a fine-tuning pipeline using LoRA (Low-Rank Adaptation) and evaluate the model's performance on both GSM8K and AILuminate datasets.

## Objectives

1. Fine-tune the Llama-3.2-1B-Instruct model on the GSM8K dataset using LoRA
2. Optimize training hyperparameters and configurations
3. Evaluate the model on GSM8K test sets (public and private)
4. Evaluate the model on the AILuminate test set
5. Generate predictions for submission

## Dataset

The following datasets are required:

- **gsm8k_train.jsonl**: Original training dataset for fine-tuning
- **gsm8k_train_self-instruct.jsonl**: Refined training dataset (optional, can be used for fine-tuning)
- **gsm8k_test_public.jsonl**: GSM8K public test dataset (with ground truth for evaluation)
- **gsm8k_test_private.jsonl**: GSM8K private test dataset (for inference only)
- **ailuminate_test.csv**: AILuminate test dataset (for inference only)

All datasets can be downloaded from:
- https://www.csie.ntu.edu.tw/~b10902031/

## Model and Framework

- **Base Model**: `meta-llama/Llama-3.2-1B-Instruct`
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
- **Quantization**: 4-bit quantization using BitsAndBytes
- **Training Framework**: Hugging Face Transformers, PEFT, and TRL

## Required Packages

Install the following packages:
```bash
pip install -U datasets trl bitsandbytes
```

Additional dependencies:
- transformers
- peft
- torch
- huggingface-hub

## Tasks to Complete

### 1. Environment Setup
- Set up HuggingFace authentication token
- Configure GPU environment
- Install required packages

### 2. Model Configuration
- Load the base model with 4-bit quantization
- Configure LoRA parameters:
  - Add dropout to LoRA configuration
  - Set appropriate target modules
- Set up tokenizer with padding token

### 3. Dataset Preparation
- Implement fixed few-shot examples (instead of random sampling)
- Format GSM8K training data with chat templates
- Handle token length to prevent truncation
- Consider using `gsm8k_train_self-instruct.jsonl` for potentially better results

### 4. Training Configuration
- Increase the number of few-shot examples for training
- If using fixed few-shot examples, increase the number of training epochs
- Decrease the learning rate for better stability
- Add weight decay to the training configuration
- Configure appropriate batch size and gradient accumulation

### 5. Inference Configuration
- Increase `max_new_tokens` for longer output generation
- Implement greedy decoding strategy (instead of sampling)
- Evaluate different checkpoint models to select the best one
- Increase the number of few-shot examples for testing

### 6. Evaluation
- Evaluate on GSM8K public test set (calculate accuracy)
- Generate predictions for GSM8K private test set
- Generate predictions for AILuminate test set

### 7. Submission
- Combine all predictions (GSM8K public + private + AILuminate)
- Save predictions to a text file named `{STUDENT_ID}.txt`
- Ensure predictions are in the correct format

## Data Format

### GSM8K Format
Each example contains:
- `question`: The math problem question
- `answer`: The solution with the final answer after `####`

### AILuminate Format
CSV file with `prompt_text` column containing the questions.

## Evaluation Metrics

- **GSM8K Public Test**: Accuracy (exact match of extracted answer)
- **GSM8K Private Test**: Predictions only (no ground truth provided)
- **AILuminate Test**: Predictions only (no ground truth provided)

## Answer Extraction

For GSM8K, extract the answer by:
1. Finding the text after `####`
2. Removing unwanted characters: `,`, `$`, `%`, `g`
3. Comparing the cleaned answer with ground truth

## Important Notes

1. Use fixed few-shot examples for consistent training and evaluation
2. Monitor training loss and adjust hyperparameters accordingly
3. The model should be fine-tuned to solve math problems while potentially forgetting previously learned knowledge about safety
4. Ensure proper handling of chat templates and tokenization
5. Remove the knowledge cutoff date information from the prompt template

## Submission Format

The submission file should contain predictions in the following order:
1. GSM8K public test predictions
2. GSM8K private test predictions  
3. AILuminate test predictions

All predictions should be in a single text file named `{STUDENT_ID}.txt`.

## References

For additional information, refer to:
- Hugging Face Transformers documentation
- PEFT library documentation
- TRL library documentation
- AILuminate dataset: https://github.com/mlcommons/ailuminate/tree/main

