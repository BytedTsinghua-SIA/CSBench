"""
Main training script for Transformer language model.

This script integrates all components to train a Transformer LM:
- Model initialization
- Data loading with memory mapping
- Training loop with checkpointing
- Validation and logging
"""

import argparse
import os
import time
import numpy as np
import torch
import torch.nn as nn

from .bpe import Tokenizer, train_bpe
from .transformer import TransformerLM
from .training import (
    cross_entropy,
    AdamW,
    get_lr_cosine_schedule,
    gradient_clipping,
    get_batch,
    save_checkpoint,
    load_checkpoint
)
from .decoding import generate_text, compute_perplexity


def train(
    # Data paths
    train_data_path: str,
    val_data_path: str,
    tokenizer_vocab_path: str = None,
    tokenizer_merges_path: str = None,
    
    # Model hyperparameters
    vocab_size: int = 10000,
    context_length: int = 256,
    num_layers: int = 4,
    d_model: int = 512,
    num_heads: int = 16,
    d_ff: int = 1344,
    rope_theta: float = 10000.0,
    
    # Training hyperparameters
    batch_size: int = 64,
    num_steps: int = 5000,
    learning_rate: float = 3e-4,
    weight_decay: float = 0.1,
    beta1: float = 0.9,
    beta2: float = 0.95,
    eps: float = 1e-8,
    max_grad_norm: float = 1.0,
    
    # Learning rate schedule
    warmup_steps: int = 100,
    min_lr: float = 1e-5,
    
    # Checkpointing
    checkpoint_dir: str = './checkpoints',
    checkpoint_interval: int = 1000,
    resume_from: str = None,
    
    # Logging
    log_interval: int = 100,
    eval_interval: int = 500,
    num_eval_batches: int = 10,
    
    # Device
    device: str = 'cpu',
    
    # Special tokens
    special_tokens: list = None
):
    """
    Main training function.
    """
    if special_tokens is None:
        special_tokens = ['<|endoftext|>']
    
    # Create checkpoint directory
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Initialize tokenizer
    if tokenizer_vocab_path and tokenizer_merges_path:
        print("Loading tokenizer from files...")
        tokenizer = Tokenizer.from_files(tokenizer_vocab_path, tokenizer_merges_path, special_tokens)
    else:
        print("Tokenizer files not provided. You need to train a tokenizer first.")
        return
    
    # Initialize model
    print("Initializing model...")
    model = TransformerLM(
        vocab_size=vocab_size,
        context_length=context_length,
        num_layers=num_layers,
        d_model=d_model,
        num_heads=num_heads,
        d_ff=d_ff,
        rope_theta=rope_theta,
        device=device
    )
    model = model.to(device)
    
    # Count parameters
    num_params = sum(p.numel() for p in model.parameters())
    print(f"Model has {num_params:,} parameters")
    
    # Initialize optimizer
    optimizer = AdamW(
        model.parameters(),
        lr=learning_rate,
        betas=(beta1, beta2),
        eps=eps,
        weight_decay=weight_decay
    )
    
    # Load checkpoint if resuming
    start_iteration = 0
    if resume_from:
        print(f"Resuming from checkpoint: {resume_from}")
        start_iteration = load_checkpoint(resume_from, model, optimizer)
        print(f"Resumed from iteration {start_iteration}")
    
    # Load data with memory mapping
    print("Loading training data...")
    train_data = np.load(train_data_path, mmap_mode='r')
    print(f"Training data shape: {train_data.shape}")
    
    print("Loading validation data...")
    val_data = np.load(val_data_path, mmap_mode='r')
    print(f"Validation data shape: {val_data.shape}")
    
    # Training loop
    print("Starting training...")
    model.train()
    
    for step in range(start_iteration, num_steps):
        # Get learning rate for this step
        current_lr = get_lr_cosine_schedule(
            step, learning_rate, min_lr, warmup_steps, num_steps
        )
        
        # Update learning rate in optimizer
        for param_group in optimizer.param_groups:
            param_group['lr'] = current_lr
        
        # Get batch
        input_ids, target_ids = get_batch(train_data, batch_size, context_length, device)
        
        # Forward pass
        logits = model(input_ids)  # (batch_size, seq_len, vocab_size)
        
        # Compute loss
        # Reshape for cross_entropy
        batch_size_actual, seq_len, vocab_size_actual = logits.shape
        logits_flat = logits.view(-1, vocab_size_actual)
        targets_flat = target_ids.view(-1)
        
        loss = cross_entropy(logits_flat, targets_flat)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping
        gradient_clipping(model.parameters(), max_grad_norm)
        
        # Optimizer step
        optimizer.step()
        
        # Logging
        if step % log_interval == 0:
            perplexity = torch.exp(loss).item()
            print(f"Step {step}/{num_steps} | "
                  f"Loss: {loss.item():.4f} | "
                  f"Perplexity: {perplexity:.4f} | "
                  f"LR: {current_lr:.2e}")
        
        # Evaluation
        if step % eval_interval == 0 and step > 0:
            model.eval()
            val_losses = []
            
            with torch.no_grad():
                for _ in range(num_eval_batches):
                    val_input, val_target = get_batch(val_data, batch_size, context_length, device)
                    val_logits = model(val_input)
                    val_logits_flat = val_logits.view(-1, vocab_size_actual)
                    val_targets_flat = val_target.view(-1)
                    val_loss = cross_entropy(val_logits_flat, val_targets_flat)
                    val_losses.append(val_loss.item())
            
            avg_val_loss = np.mean(val_losses)
            val_perplexity = np.exp(avg_val_loss)
            print(f"Validation | Loss: {avg_val_loss:.4f} | Perplexity: {val_perplexity:.4f}")
            
            # Generate sample text
            sample_text = generate_text(
                model, tokenizer, "Once upon a time",
                max_tokens=50, temperature=0.8, top_p=0.9, device=device
            )
            print(f"Sample generation: {sample_text[:200]}...")
            
            model.train()
        
        # Checkpointing
        if step % checkpoint_interval == 0 and step > 0:
            checkpoint_path = os.path.join(checkpoint_dir, f"checkpoint_step_{step}.pt")
            save_checkpoint(model, optimizer, step, checkpoint_path)
            print(f"Saved checkpoint to {checkpoint_path}")
    
    # Final checkpoint
    final_checkpoint_path = os.path.join(checkpoint_dir, "checkpoint_final.pt")
    save_checkpoint(model, optimizer, num_steps, final_checkpoint_path)
    print(f"Training complete! Final checkpoint saved to {final_checkpoint_path}")


def main():
    """
    Main entry point with argument parsing.
    """
    parser = argparse.ArgumentParser(description='Train Transformer Language Model')
    
    # Data paths
    parser.add_argument('--train_data_path', type=str, required=True,
                       help='Path to training tokenized data (numpy array)')
    parser.add_argument('--val_data_path', type=str, required=True,
                       help='Path to validation tokenized data (numpy array)')
    parser.add_argument('--tokenizer_vocab_path', type=str, required=True,
                       help='Path to tokenizer vocabulary file')
    parser.add_argument('--tokenizer_merges_path', type=str, required=True,
                       help='Path to tokenizer merges file')
    
    # Model hyperparameters
    parser.add_argument('--vocab_size', type=int, default=10000)
    parser.add_argument('--context_length', type=int, default=256)
    parser.add_argument('--num_layers', type=int, default=4)
    parser.add_argument('--d_model', type=int, default=512)
    parser.add_argument('--num_heads', type=int, default=16)
    parser.add_argument('--d_ff', type=int, default=1344)
    parser.add_argument('--rope_theta', type=float, default=10000.0)
    
    # Training hyperparameters
    parser.add_argument('--batch_size', type=int, default=64)
    parser.add_argument('--num_steps', type=int, default=5000)
    parser.add_argument('--learning_rate', type=float, default=3e-4)
    parser.add_argument('--weight_decay', type=float, default=0.1)
    parser.add_argument('--beta1', type=float, default=0.9)
    parser.add_argument('--beta2', type=float, default=0.95)
    parser.add_argument('--eps', type=float, default=1e-8)
    parser.add_argument('--max_grad_norm', type=float, default=1.0)
    
    # Learning rate schedule
    parser.add_argument('--warmup_steps', type=int, default=100)
    parser.add_argument('--min_lr', type=float, default=1e-5)
    
    # Checkpointing
    parser.add_argument('--checkpoint_dir', type=str, default='./checkpoints')
    parser.add_argument('--checkpoint_interval', type=int, default=1000)
    parser.add_argument('--resume_from', type=str, default=None)
    
    # Logging
    parser.add_argument('--log_interval', type=int, default=100)
    parser.add_argument('--eval_interval', type=int, default=500)
    parser.add_argument('--num_eval_batches', type=int, default=10)
    
    # Device
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda', 'mps'],
                       help='Device to use for training')
    
    args = parser.parse_args()
    
    # Run training
    train(
        train_data_path=args.train_data_path,
        val_data_path=args.val_data_path,
        tokenizer_vocab_path=args.tokenizer_vocab_path,
        tokenizer_merges_path=args.tokenizer_merges_path,
        vocab_size=args.vocab_size,
        context_length=args.context_length,
        num_layers=args.num_layers,
        d_model=args.d_model,
        num_heads=args.num_heads,
        d_ff=args.d_ff,
        rope_theta=args.rope_theta,
        batch_size=args.batch_size,
        num_steps=args.num_steps,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        beta1=args.beta1,
        beta2=args.beta2,
        eps=args.eps,
        max_grad_norm=args.max_grad_norm,
        warmup_steps=args.warmup_steps,
        min_lr=args.min_lr,
        checkpoint_dir=args.checkpoint_dir,
        checkpoint_interval=args.checkpoint_interval,
        resume_from=args.resume_from,
        log_interval=args.log_interval,
        eval_interval=args.eval_interval,
        num_eval_batches=args.num_eval_batches,
        device=args.device
    )


if __name__ == '__main__':
    main()

