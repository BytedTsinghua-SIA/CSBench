from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _load_cifar_small(num_train=200, num_val=100):
    _ensure_project_root_on_path()
    from project.data_utils import load_CIFAR10

    root = Path(__file__).resolve().parent.parent
    cifar_dir = root / "datasets" / "cifar-10-batches-py"
    X_all, y_all, X_test_all, y_test_all = load_CIFAR10(str(cifar_dir))

    X_train_raw = X_all[:num_train]
    y_train = y_all[:num_train]
    X_val_raw = X_all[num_train : num_train + num_val]
    y_val = y_all[num_train : num_train + num_val]
    X_test_raw = X_test_all[:num_val]
    y_test = y_test_all[:num_val]

    mean_image = np.mean(X_train_raw, axis=0)
    X_train = (X_train_raw - mean_image).reshape(num_train, -1)
    X_val = (X_val_raw - mean_image).reshape(num_val, -1)
    X_test = (X_test_raw - mean_image).reshape(num_val, -1)

    return X_train, y_train, X_val, y_val, X_test, y_test


def test_two_layer_net_cifar_training_with_solver():
    _ensure_project_root_on_path()
    from project.classifiers.fc_net import TwoLayerNet
    from project.solver import Solver

    X_train, y_train, X_val, y_val, X_test, y_test = _load_cifar_small()

    np.random.seed(1)
    model = TwoLayerNet(
        input_dim=X_train.shape[1],
        hidden_dim=50,
        num_classes=10,
        weight_scale=1e-2,
        reg=0.0,
    )

    data = {
        "X_train": X_train,
        "y_train": y_train,
        "X_val": X_val,
        "y_val": y_val,
    }

    solver = Solver(
        model,
        data,
        update_rule="sgd",
        optim_config={"learning_rate": 1e-3},
        num_epochs=1,
        batch_size=100,
        print_every=1000,
        verbose=False,
    )

    solver.train()

    # Basic checks that training makes progress at some point.
    assert len(solver.loss_history) > 0
    first_loss = solver.loss_history[0]
    min_loss = min(solver.loss_history)
    assert min_loss < first_loss

    final_val_acc = solver.val_acc_history[-1]
    assert final_val_acc >= 0.15
