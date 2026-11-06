from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _softmax_loss_reference(W, X, y, reg):
    scores = X.dot(W)
    scores -= scores.max(axis=1, keepdims=True)
    exp_scores = np.exp(scores)
    probs = exp_scores / exp_scores.sum(axis=1, keepdims=True)
    N = X.shape[0]
    correct = -np.log(probs[np.arange(N), y])
    data_loss = correct.mean()
    reg_loss = reg * np.sum(W * W)
    loss = data_loss + reg_loss

    dscores = probs
    dscores[np.arange(N), y] -= 1.0
    dscores /= N
    dW = X.T.dot(dscores) + 2.0 * reg * W
    return loss, dW


def test_softmax_naive_matches_reference():
    _ensure_project_root_on_path()
    from project.classifiers.softmax import softmax_loss_naive

    np.random.seed(0)
    N, D, C = 4, 5, 3
    X = 0.01 * np.random.randn(N, D)
    W = 0.01 * np.random.randn(D, C)
    y = np.array([0, 1, 2, 1], dtype=np.int64)
    reg = 0.1

    ref_loss, ref_dW = _softmax_loss_reference(W, X, y, reg)
    loss, dW = softmax_loss_naive(W, X, y, reg)

    assert np.allclose(loss, ref_loss, rtol=1e-6, atol=1e-6)
    assert np.allclose(dW, ref_dW, rtol=1e-5, atol=1e-5)


def test_softmax_vectorized_matches_naive():
    _ensure_project_root_on_path()
    from project.classifiers.softmax import softmax_loss_naive, softmax_loss_vectorized

    np.random.seed(1)
    N, D, C = 6, 4, 3
    X = 0.01 * np.random.randn(N, D)
    W = 0.01 * np.random.randn(D, C)
    y = np.array([1, 0, 2, 1, 2, 0], dtype=np.int64)
    reg = 0.05

    loss_naive, dW_naive = softmax_loss_naive(W, X, y, reg)
    loss_vec, dW_vec = softmax_loss_vectorized(W, X, y, reg)

    assert np.allclose(loss_naive, loss_vec, rtol=1e-7, atol=1e-7)
    assert np.allclose(dW_naive, dW_vec, rtol=1e-6, atol=1e-6)
