import math

import torch

from optimizer import AdamW


def test_adamw_step_matches_manual_update():
    param = torch.nn.Parameter(torch.tensor([0.5, -0.25]))
    optimizer = AdamW([param], lr=0.1, betas=(0.9, 0.99), eps=1e-8, weight_decay=0.01)

    grad = torch.tensor([0.2, -0.3])
    param.grad = grad.clone()
    initial = param.data.clone()

    optimizer.step()

    beta1, beta2 = optimizer.param_groups[0]["betas"]
    lr = optimizer.param_groups[0]["lr"]
    eps = optimizer.param_groups[0]["eps"]
    weight_decay = optimizer.param_groups[0]["weight_decay"]

    grad_t = grad + weight_decay * initial
    m = (1 - beta1) * grad_t
    v = (1 - beta2) * grad_t.pow(2)
    alpha_t = lr * math.sqrt(1 - beta2 ** 1) / (1 - beta1 ** 1)
    expected = initial - (alpha_t * m) / (torch.sqrt(v) + eps) - alpha_t * weight_decay * initial

    assert torch.allclose(param.data, expected, atol=1e-8)
