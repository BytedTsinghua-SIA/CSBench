from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def test_fully_connected_net_forward_backward_small_net():
    _ensure_project_root_on_path()
    from project.classifiers.fc_net import FullyConnectedNet
    from project.gradient_check import eval_numerical_gradient

    np.random.seed(1)
    N, D, C = 2, 4, 3
    X = 0.01 * np.random.randn(N, D)
    y = np.array([0, 2], dtype=np.int64)

    model = FullyConnectedNet([5], input_dim=D, num_classes=C, weight_scale=1e-1, reg=0.0)

    loss, grads = model.loss(X, y)
    assert isinstance(loss, float)

    assert len(model.params) > 0

    for p, w in model.params.items():
        if not p.startswith("W") and not p.startswith("b"):
            continue

        def loss_fn(w_local):
            old = model.params[p]
            model.params[p] = w_local
            l, _ = model.loss(X, y)
            model.params[p] = old
            return l

        grad_num = eval_numerical_gradient(loss_fn, w, verbose=False)
        grad_an = grads[p]
        rel_err = np.max(
            np.abs(grad_num - grad_an)
            / np.maximum(1e-8, np.abs(grad_num) + np.abs(grad_an))
        )
        assert rel_err < 1e-3


def test_optim_update_rules_move_in_negative_gradient_direction():
    _ensure_project_root_on_path()
    from project import optim

    np.random.seed(2)
    w = np.array([1.0, -2.0, 3.0])
    dw = np.array([0.1, -0.2, 0.3])

    next_w_sgd, _ = optim.sgd(w.copy(), dw.copy(), {"learning_rate": 1.0})
    assert np.allclose(next_w_sgd, w - dw)

    next_w_mom, cfg_m = optim.sgd_momentum(w.copy(), dw.copy(), {"learning_rate": 1.0, "momentum": 0.9})
    assert next_w_mom.shape == w.shape

    next_w_rms, cfg_r = optim.rmsprop(w.copy(), dw.copy(), {"learning_rate": 1.0})
    assert next_w_rms.shape == w.shape

    next_w_adam, cfg_a = optim.adam(w.copy(), dw.copy(), {"learning_rate": 1.0})
    assert next_w_adam.shape == w.shape
