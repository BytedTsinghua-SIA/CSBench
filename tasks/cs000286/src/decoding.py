import torch
import torch.nn as nn
from typing import Optional, List
from .transformer import softmax


def temperature_scaled_softmax(logits: torch.Tensor, temperature: float) -> torch.Tensor:
    pass


def top_p_sampling(
    probs: torch.Tensor,
    top_p: float
) -> torch.Tensor:
    pass


def generate_text(
    model: nn.Module,
    tokenizer,
    prompt: str,
    max_tokens: int = 256,
    temperature: float = 1.0,
    top_p: Optional[float] = None,
    end_token: str = "<|endoftext|>",
    device: str = 'cpu'
) -> str:
    pass


def compute_perplexity(
    model: nn.Module,
    tokenizer,
    text: str,
    device: str = 'cpu'
) -> float:
    pass
