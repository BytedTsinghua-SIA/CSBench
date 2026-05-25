from pathlib import Path
import importlib
import inspect
import sys


def _ensure_project_root_on_path():
    """Ensure the repository root (containing project/ and tests/) is on sys.path."""
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def test_q1_knn_module_and_api_exist():
    _ensure_project_root_on_path()

    knn_mod = importlib.import_module("project.classifiers.k_nearest_neighbor")

    for name in [
        "compute_distances_two_loops",
        "compute_distances_one_loop",
        "compute_distances_no_loops",
        "predict_labels",
    ]:
        assert hasattr(knn_mod.KNearestNeighbor, name)
        attr = getattr(knn_mod.KNearestNeighbor, name)
        assert callable(attr)
    data_utils = importlib.import_module("project.data_utils")
    assert hasattr(data_utils, "load_CIFAR10")


def test_q2_softmax_and_linear_classifier_api_exist():
    _ensure_project_root_on_path()
    softmax_mod = importlib.import_module("project.classifiers.softmax")
    lincls_mod = importlib.import_module("project.classifiers.linear_classifier")

    for name in ["softmax_loss_naive", "softmax_loss_vectorized"]:
        assert hasattr(softmax_mod, name)
        assert callable(getattr(softmax_mod, name))

    assert hasattr(lincls_mod, "LinearClassifier")
    assert hasattr(lincls_mod, "LinearSVM")
    assert hasattr(lincls_mod, "Softmax")

    cls = lincls_mod.LinearClassifier
    for name in ["train", "predict", "loss"]:
        assert hasattr(cls, name)
        assert callable(getattr(cls, name))


def test_q3_two_layer_net_and_solver_exist():
    _ensure_project_root_on_path()
    fc_mod = importlib.import_module("project.classifiers.fc_net")
    solver_mod = importlib.import_module("project.solver")

    assert hasattr(fc_mod, "TwoLayerNet")
    two_cls = fc_mod.TwoLayerNet
    assert inspect.isclass(two_cls)

    for name in ["__init__", "loss"]:
        assert hasattr(two_cls, name)

    assert hasattr(solver_mod, "Solver")
    assert inspect.isclass(solver_mod.Solver)


def test_q4_features_api_exist():
    _ensure_project_root_on_path()
    feats_mod = importlib.import_module("project.features")

    for name in [
        "extract_features",
        "hog_feature",
        "color_histogram_hsv",
    ]:
        assert hasattr(feats_mod, name)
        assert callable(getattr(feats_mod, name))


def test_q5_fully_connected_net_layers_and_optim_exist():
    _ensure_project_root_on_path()
    fc_mod = importlib.import_module("project.classifiers.fc_net")
    layers_mod = importlib.import_module("project.layers")
    optim_mod = importlib.import_module("project.optim")

    assert hasattr(fc_mod, "FullyConnectedNet")
    fc_cls = fc_mod.FullyConnectedNet
    assert inspect.isclass(fc_cls)
    for name in ["__init__", "loss"]:
        assert hasattr(fc_cls, name)

    for name in [
        "layernorm_forward",
        "layernorm_backward",
        "dropout_forward",
        "dropout_backward",
    ]:
        assert hasattr(layers_mod, name)
        assert callable(getattr(layers_mod, name))

    for name in ["sgd_momentum", "rmsprop", "adam"]:
        assert hasattr(optim_mod, name)
        assert callable(getattr(optim_mod, name))
