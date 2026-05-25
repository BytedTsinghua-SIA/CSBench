"""
LLM Transformers Understanding Module
实现ML_HW3中要求的所有功能
"""

from .llm_utils import (
    generate_text_from_prompt,
    tokenize_sentence,
    generate_with_top_p,
    extract_model_outputs,
    get_max_activation,
    plot_token_activations,
    plot_layer_activations,
    compute_self_bleu,
)

__all__ = [
    'generate_text_from_prompt',
    'tokenize_sentence',
    'generate_with_top_p',
    'extract_model_outputs',
    'get_max_activation',
    'plot_token_activations',
    'plot_layer_activations',
    'compute_self_bleu',
]

