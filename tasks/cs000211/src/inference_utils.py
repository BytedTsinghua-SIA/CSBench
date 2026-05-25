"""
Inference utilities: model inference and output parsing
"""

import json
import torch
from typing import Dict, Any, List

# Support both relative and absolute imports
try:
    from .config import InferenceConfig
except ImportError:
    from config import InferenceConfig


def parse_true_output(text: str) -> str:
    """
    Extract the true assistant output from decoded model output

    Find assistant header token:
        "<|start_header_id|>assistant<|end_header_id|>\n\n"
    and extract all content after it until the first "<|eot_id|>".
    If assistant header is not found, fall back to the last occurrence of
    "<|end_header_id|>\n\n".
    If "<|eot_id|>" is not found, extract to the end of the string.

    Args:
        text: Decoded model output

    Returns:
        Extracted assistant response text
    """
    pass


def generate_response(
    model,
    tokenizer,
    messages: List[Dict[str, str]],
    inference_config: InferenceConfig,
    device: str = "cuda",
) -> str:
    """
    Generate model response

    Args:
        model: Model object
        tokenizer: Tokenizer object
        messages: Message list, format: [{"role": "user", "content": "..."}]
        inference_config: Inference configuration
        device: Device ("cuda" or "cpu")

    Returns:
        Generated response text
    """
    pass


def run_inference_on_test_set(
    model,
    tokenizer,
    test_set_path: str,
    inference_config: InferenceConfig,
    output_path: str = "pred.json",
    device: str = "cuda",
) -> Dict[str, Any]:
    """
    Run inference on test set

    Args:
        model: Model object
        tokenizer: Tokenizer object
        test_set_path: Test set JSON file path
        inference_config: Inference configuration
        output_path: Output JSON file path
        device: Device

    Returns:
        Inference results dictionary
    """
    pass
