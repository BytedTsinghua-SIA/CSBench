from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _load_cifar_small(num_train=200, num_val=100, num_test=100):
    _ensure_project_root_on_path()
    from project.data_utils import load_CIFAR10

    root = Path(__file__).resolve().parent.parent
    cifar_dir = root / "datasets" / "cifar-10-batches-py"
    X_all, y_all, X_test_all, y_test_all = load_CIFAR10(str(cifar_dir))

    X_train = X_all[:num_train].reshape(num_train, -1)
    y_train = y_all[:num_train]
    X_val = X_all[num_train : num_train + num_val].reshape(num_val, -1)
    y_val = y_all[num_train : num_train + num_val]
    X_test = X_test_all[:num_test].reshape(num_test, -1)
    y_test = y_test_all[:num_test]
    return X_train, y_train, X_val, y_val, X_test, y_test


def test_knn_cifar_cross_validation_pipeline():
    _ensure_project_root_on_path()
    from project.classifiers.k_nearest_neighbor import KNearestNeighbor

    X_train, y_train, X_val, y_val, X_test, y_test = _load_cifar_small()

    # Merge train/val for K-fold over training set as described in task.md.
    X_all = np.vstack([X_train, X_val])
    y_all = np.concatenate([y_train, y_val])

    num_folds = 5
    k_choices = [1, 3, 5]
    indices = np.arange(X_all.shape[0])
    folds = np.array_split(indices, num_folds)

    k_to_accuracies = {k: [] for k in k_choices}

    for k in k_choices:
        for i in range(num_folds):
            val_idx = folds[i]
            train_idx = np.concatenate([folds[j] for j in range(num_folds) if j != i])

            X_tr, y_tr = X_all[train_idx], y_all[train_idx]
            X_va, y_va = X_all[val_idx], y_all[val_idx]

            knn = KNearestNeighbor()
            knn.train(X_tr, y_tr)
            dists = knn.compute_distances_no_loops(X_va)
            y_pred = knn.predict_labels(dists, k=k)
            acc = np.mean(y_pred == y_va)
            k_to_accuracies[k].append(acc)

    # Pick the best k based on average validation accuracy.
    best_k = max(k_choices, key=lambda kk: np.mean(k_to_accuracies[kk]))
    assert best_k in k_choices

    # Train on full training set with best k and evaluate on held-out test set.
    knn_final = KNearestNeighbor()
    knn_final.train(X_all, y_all)
    dists_test = knn_final.compute_distances_no_loops(X_test)
    y_test_pred = knn_final.predict_labels(dists_test, k=best_k)

    test_acc = np.mean(y_test_pred == y_test)
    # Should be significantly better than random (10% for 10-way classification).
    assert test_acc >= 0.18
