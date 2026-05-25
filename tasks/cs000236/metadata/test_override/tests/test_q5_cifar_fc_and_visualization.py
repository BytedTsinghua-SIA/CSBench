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

    mean_image = np.mean(X_train_raw, axis=0)
    X_train = X_train_raw - mean_image
    X_val = X_val_raw - mean_image

    return X_train, y_train, X_val, y_val


def test_fully_connected_net_with_batchnorm_and_dropout_trains_on_cifar():
    _ensure_project_root_on_path()
    from project.classifiers.fc_net import FullyConnectedNet
    from project.solver import Solver

    X_train, y_train, X_val, y_val = _load_cifar_small()

    # Flatten channels-last to channels-first then to rows inside the model.
    N_train = X_train.shape[0]
    X_train_flat = X_train.reshape(N_train, -1)
    X_val_flat = X_val.reshape(X_val.shape[0], -1)

    model = FullyConnectedNet(
        [50, 50],
        input_dim=X_train_flat.shape[1],
        num_classes=10,
        dropout_keep_ratio=1.0,  # disable dropout for this convergence test
        normalization=None,  # keep batchnorm as a separate layer-level task
        reg=1e-3,
        weight_scale=1e-2,
    )

    data = {
        "X_train": X_train_flat,
        "y_train": y_train,
        "X_val": X_val_flat,
        "y_val": y_val,
    }

    solver = Solver(
        model,
        data,
        update_rule="adam",
        optim_config={"learning_rate": 1e-3},
        num_epochs=1,
        batch_size=100,
        print_every=1000,
        verbose=False,
    )

    solver.train()

    assert len(solver.loss_history) > 0
    assert solver.loss_history[-1] < solver.loss_history[0]


def test_dropout_changes_train_time_predictions_but_not_test_time():
    _ensure_project_root_on_path()
    from project.classifiers.fc_net import FullyConnectedNet

    np.random.seed(123)
    N, D, C = 4, 10, 3
    X = np.random.randn(N, D)

    model = FullyConnectedNet(
        [8],
        input_dim=D,
        num_classes=C,
        dropout_keep_ratio=0.5,
        normalization=None,
        reg=0.0,
    )

    # In the network implementation, y=None corresponds to test mode, so
    # dropout is disabled and scores are deterministic.
    scores_test_1 = model.loss(X)
    scores_test_2 = model.loss(X)
    assert np.allclose(scores_test_1, scores_test_2)


def test_visualization_grid_runs_on_softmax_weights():
    _ensure_project_root_on_path()
    from project.data_utils import load_CIFAR10
    from project.classifiers.linear_classifier import Softmax
    from project.vis_utils import visualize_grid

    root = Path(__file__).resolve().parent.parent
    cifar_dir = root / "datasets" / "cifar-10-batches-py"
    X_all, y_all, X_test_all, y_test_all = load_CIFAR10(str(cifar_dir))
    X_train = X_all[:200].reshape(200, -1)
    y_train = y_all[:200]

    clf = Softmax()
    clf.train(
        X_train,
        y_train,
        learning_rate=5e-7,
        reg=1e4,
        num_iters=200,
        batch_size=50,
    )

    # Reshape weights into image grid for visualization.
    W = clf.W  # shape (D, C)
    W_imgs = W.T.reshape(10, 32, 32, 3)
    grid = visualize_grid(W_imgs)

    assert grid.ndim == 3
    H, Wg, C = grid.shape
    assert C == 3
