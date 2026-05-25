"""LLM interface for generating responses."""

from typing import Any, Optional


def generate_response(
    model: Any, 
    _messages: list[dict[str, str]], 
    stop: Optional[list[str]] = None,
    max_tokens: int = 4096,
    temperature: float = 0
) -> str:
    raise NotImplementedError

