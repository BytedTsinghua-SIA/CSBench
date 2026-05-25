"""
Benchmarking script for Transformer model forward and backward passes.
"""

import argparse
import timeit
from typing import Literal

import torch

from cs336_basics.model import BasicsTransformerLM


def get_model_config(model_size: str):
    """Get model configuration based on model size name."""
    pass


def benchmark_model(
    model: torch.nn.Module,
    batch_size: int,
    context_length: int,
    vocab_size: int,
    warmup_steps: int,
    num_steps: int,
    mode: Literal["forward", "forward_backward"],
    device: str = "cuda",
):
    """
    Benchmark forward and/or backward passes of a model.

    Args:
        model: The model to benchmark
        batch_size: Batch size for the input
        context_length: Sequence length
        vocab_size: Vocabulary size
        warmup_steps: Number of warmup steps before timing
        num_steps: Number of steps to time
        mode: Either "forward" or "forward_backward"
        device: Device to run on

    Returns:
        List of timing results in seconds
    """
    pass


def main():
    pass


if __name__ == "__main__":
    main()
