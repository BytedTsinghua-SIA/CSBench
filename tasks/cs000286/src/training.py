import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
from typing import Optional, Tuple, BinaryIO, Union, List
from collections.abc import Callable, Iterable


def cross_entropy(logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    pass


def get_lr_cosine_schedule(
    t: int,
    alpha_max: float,
    alpha_min: float,
    T_w: int,
    T_c: int
) -> float:
    pass


def gradient_clipping(parameters: Iterable[torch.nn.Parameter], max_norm: float):
    pass


class AdamW(optim.Optimizer):
    def __init__(
        self,
        params,
        lr: float = 1e-3,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.01
    ):
        defaults = {'lr': lr, 'betas': betas, 'eps': eps, 'weight_decay': weight_decay}
        super().__init__(params, defaults)
    
    def step(self, closure: Optional[Callable] = None):
        pass


def get_batch(
    data: np.ndarray,
    batch_size: int,
    context_length: int,
    device: str = 'cpu'
) -> Tuple[torch.Tensor, torch.Tensor]:
    pass


def save_checkpoint(
    model: nn.Module,
    optimizer: optim.Optimizer,
    iteration: int,
    out: Union[str, os.PathLike, BinaryIO]
):
    pass


def load_checkpoint(
    src: Union[str, os.PathLike, BinaryIO],
    model: nn.Module,
    optimizer: optim.Optimizer
) -> int:
    pass
