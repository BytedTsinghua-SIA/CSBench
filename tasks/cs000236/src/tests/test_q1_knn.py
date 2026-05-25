from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _make_knn():
    _ensure_project_root_on_path()
    from project.classifiers.k_nearest_neighbor import KNearestNeighbor

    X_train = np.array(
        [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]], dtype=np.float64
    )
    y_train = np.array([0, 0, 1, 1], dtype=np.int64)
    knn = KNearestNeighbor()
    knn.train(X_train, y_train)
    return knn, X_train, y_train


def test_knn_distance_implementations_match():
    knn, _, _ = _make_knn()
    X_test = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float64)

    d_two = knn.compute_distances_two_loops(X_test)
    d_one = knn.compute_distances_one_loop(X_test)
    d_none = knn.compute_distances_no_loops(X_test)

    assert d_two.shape == (2, 4)
    assert np.allclose(d_two, d_one)
    assert np.allclose(d_two, d_none)

    expected = np.array(
        [
            [0.0, 1.0, 1.0, np.sqrt(2.0)],
            [np.sqrt(2.0), 1.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )
    assert np.allclose(d_two, expected, rtol=1e-6, atol=1e-6)


def test_knn_predict_labels_for_small_example():
    knn, _, _ = _make_knn()
    X_test = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float64)
    dists = knn.compute_distances_two_loops(X_test)

    y_k1 = knn.predict_labels(dists, k=1)
    y_k3 = knn.predict_labels(dists, k=3)

    assert y_k1.shape == (2,)
    assert y_k3.shape == (2,)
    assert y_k1[0] == 0
    assert y_k1[1] == 1
    assert y_k3[0] == 0
    assert y_k3[1] == 1
