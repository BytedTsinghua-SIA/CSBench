"""
Main program entry point
"""
import argparse
import os
import torch
from pathlib import Path

from .config import Config
from .model_utils import (
    setup_device,
    load_model_and_tokenizer,
    create_generation_pipeline,
    load_adapter
)
from .trainer import format_gsm8k_data, create_trainer
from .inference import (
    evaluate_gsm8k_public,
    infer_gsm8k_private,
    evaluate_ailuminate
)


def train(config: Config, train_file: str):
    """
    Train model
    
    Args:
        config: Configuration object
        train_file: Training data file path
    """
    print("=" * 50)
    print("Starting training")
    print("=" * 50)
    
    # Setup device
    device = setup_device(config.cuda_device)
    
    # Load model and tokenizer
    print("Loading model and tokenizer...")
    model, tokenizer, peft_config = load_model_and_tokenizer(
        config.model,
        config.lora
    )
    
    # Format training data
    print("Formatting training data...")
    train_dataset, max_token_len = format_gsm8k_data(
        tokenizer,
        train_file,
        config.data
    )
    print(f"Maximum token length: {max_token_len}")
    
    # Create trainer
    print("Creating trainer...")
    trainer = create_trainer(
        model,
        tokenizer,
        train_dataset,
        config.training,
        config.lora,
        max_token_len
    )
    
    # Start training
    print("Starting training...")
    trainer.train()
    
    print("Training completed!")
    return trainer


def inference(
    config: Config,
    adapter_path: str,
    gsm8k_test_public: str,
    gsm8k_test_private: str,
    gsm8k_train: str,
    ailuminate_test: str,
    output_file: str = None
):
    """
    Perform inference
    
    Args:
        config: Configuration object
        adapter_path: Adapter path
        gsm8k_test_public: GSM8K public test set path
        gsm8k_test_private: GSM8K private test set path
        gsm8k_train: GSM8K training set path (for few-shot)
        ailuminate_test: AILuminate test set path
        output_file: Output file path
    """
    print("=" * 50)
    print("Starting inference")
    print("=" * 50)
    
    # Setup device
    device = setup_device(config.cuda_device)
    
    # Load model and tokenizer
    print("Loading model and tokenizer...")
    model, tokenizer, _ = load_model_and_tokenizer(
        config.model,
        config.lora
    )
    
    # Load adapter
    print(f"Loading adapter: {adapter_path}")
    model = load_adapter(model, adapter_path)
    
    # Create generation pipeline
    print("Creating generation pipeline...")
    generator = create_generation_pipeline(
        model,
        tokenizer,
        config.inference,
        device
    )
    
    # Prepare fixed few-shot examples
    fixed_examples = None
    if config.data.use_fixed_few_shot:
        from .data_utils import load_jsonlines
        gsm8k_train_data = load_jsonlines(gsm8k_train)
        fixed_examples = gsm8k_train_data[:config.data.fixed_few_shot_size]
    
    # Evaluate GSM8K public test set
    print("\nEvaluating GSM8K public test set...")
    gsm8k_public_predictions, accuracy = evaluate_gsm8k_public(
        generator,
        gsm8k_test_public,
        gsm8k_train,
        config.data,
        fixed_examples
    )
    
    # Infer GSM8K private test set
    print("\nInferring GSM8K private test set...")
    gsm8k_private_predictions = infer_gsm8k_private(
        generator,
        gsm8k_test_private,
        gsm8k_train,
        config.data,
        fixed_examples
    )
    
    # Evaluate AILuminate
    print("\nEvaluating AILuminate test set...")
    ailuminate_predictions = evaluate_ailuminate(
        generator,
        ailuminate_test
    )
    
    # Merge all prediction results
    all_predictions = gsm8k_public_predictions + gsm8k_private_predictions + ailuminate_predictions
    
    # Save results
    if output_file:
        print(f"\nSaving results to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            print(all_predictions, file=f)
    else:
        # Use student_id as filename
        if config.student_id:
            output_file = f"{config.student_id}.txt"
            print(f"\nSaving results to: {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                print(all_predictions, file=f)
        else:
            print("\nWarning: student_id not set, results not saved")
    
    print("\nInference completed!")
    return all_predictions


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='ML2025 Homework 6 - Fine-tuning')
    parser.add_argument('--mode', type=str, choices=['train', 'inference', 'both'], 
                       default='both', help='Run mode')
    parser.add_argument('--train_file', type=str, default='gsm8k_train.jsonl',
                       help='Training data file path')
    parser.add_argument('--gsm8k_test_public', type=str, default='gsm8k_test_public.jsonl',
                       help='GSM8K public test set path')
    parser.add_argument('--gsm8k_test_private', type=str, default='gsm8k_test_private.jsonl',
                       help='GSM8K private test set path')
    parser.add_argument('--ailuminate_test', type=str, default='ailuminate_test.csv',
                       help='AILuminate test set path')
    parser.add_argument('--adapter_path', type=str, default='sft/checkpoint-1868',
                       help='Adapter path')
    parser.add_argument('--output_file', type=str, default=None,
                       help='Output file path')
    parser.add_argument('--student_id', type=str, default='',
                       help='Student ID')
    parser.add_argument('--config', type=str, default=None,
                       help='Configuration file path (JSON format)')
    
    args = parser.parse_args()
    
    # Create configuration
    config = Config()
    config.student_id = args.student_id
    
    # If config file is provided, can load it here
    # if args.config:
    #     import json
    #     with open(args.config, 'r') as f:
    #         config_dict = json.load(f)
    #     # Update configuration...
    
    # Run training
    if args.mode in ['train', 'both']:
        train(config, args.train_file)
    
    # Run inference
    if args.mode in ['inference', 'both']:
        inference(
            config,
            args.adapter_path,
            args.gsm8k_test_public,
            args.gsm8k_test_private,
            args.train_file,
            args.ailuminate_test,
            args.output_file
        )


if __name__ == '__main__':
    main()

