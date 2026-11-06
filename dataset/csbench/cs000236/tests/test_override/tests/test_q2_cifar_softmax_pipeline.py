from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _load_cifar_small(num_train=500, num_val=200, num_test=200):
    _ensure_project_root_on_path()
    from project.data_utils import load_CIFAR10

    root = Path(__file__).resolve().parent.parent
    cifar_dir = root / "datasets" / "cifar-10-batches-py"
    X_all, y_all, X_test_all, y_test_all = load_CIFAR10(str(cifar_dir))

    # Use a contiguous chunk for train/val/test.
    X_train_raw = X_all[:num_train]
    y_train = y_all[:num_train]
    X_val_raw = X_all[num_train : num_train + num_val]
    y_val = y_all[num_train : num_train + num_val]
    X_test_raw = X_test_all[:num_test]
    y_test = y_test_all[:num_test]

    # Subtract mean image over training set, as in get_CIFAR10_data.
    mean_image = np.mean(X_train_raw, axis=0)
    X_train = (X_train_raw - mean_image).reshape(num_train, -1)
    X_val = (X_val_raw - mean_image).reshape(num_val, -1)
    X_test = (X_test_raw - mean_image).reshape(num_test, -1)
    return X_train, y_train, X_val, y_val, X_test, y_test


def test_softmax_cifar_training_pipeline():
    _ensure_project_root_on_path()
    from project.classifiers.linear_classifier import Softmax

    X_train, y_train, X_val, y_val, X_test, y_test = _load_cifar_small()

    np.random.seed(0)
    clf = Softmax()
    # Hyperparameters chosen to converge quickly on the small subset.
    loss_hist = clf.train(
        X_train,
        y_train,
        learning_rate=5e-7,
        reg=2.5e4,
        num_iters=700,
        batch_size=200,
    )

    # Loss should decrease over training.
    assert len(loss_hist) > 1
    assert loss_hist[-1] < loss_hist[0]

    y_val_pred = clf.predict(X_val)
    val_acc = np.mean(y_val_pred == y_val)
    # Softmax on CIFAR-10 subset should do better than random guessing.
    assert val_acc >= 0.18
