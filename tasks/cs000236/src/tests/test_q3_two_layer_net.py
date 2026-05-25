from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def test_two_layer_net_forward_backward_consistency():
    _ensure_project_root_on_path()
    from project.classifiers.fc_net import TwoLayerNet
    from project.gradient_check import eval_numerical_gradient

    np.random.seed(0)
    N, D, H, C = 3, 4, 5, 3
    X = 0.1 * np.random.randn(N, D)
    y = np.array([0, 1, 2], dtype=np.int64)

    model = TwoLayerNet(input_dim=D, hidden_dim=H, num_classes=C, weight_scale=1e-1)

    loss, grads = model.loss(X, y)
    assert isinstance(loss, float)
    params = ["W1", "b1", "W2", "b2"]

    for p in params:
        def loss_fn(w):
            old = model.params[p]
            model.params[p] = w
            l, _ = model.loss(X, y)
            model.params[p] = old
            return l

        w = model.params[p]
        grad_num = eval_numerical_gradient(loss_fn, w, verbose=False)
        grad_an = grads[p]
        rel_err = np.max(np.abs(grad_num - grad_an) / np.maximum(1e-8, np.abs(grad_num) + np.abs(grad_an)))
        assert rel_err < 1e-4
