from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _load_cifar_small(num_train=400, num_val=100):
    _ensure_project_root_on_path()
    from project.data_utils import load_CIFAR10

    root = Path(__file__).resolve().parent.parent
    cifar_dir = root / "datasets" / "cifar-10-batches-py"
    X_all, y_all, X_test_all, y_test_all = load_CIFAR10(str(cifar_dir))

    X_train = X_all[:num_train]
    y_train = y_all[:num_train]
    X_val = X_all[num_train : num_train + num_val]
    y_val = y_all[num_train : num_train + num_val]
    return X_train, y_train, X_val, y_val


def test_cifar_features_improve_over_raw_pixels():
    _ensure_project_root_on_path()
    from project.features import extract_features, hog_feature, color_histogram_hsv
    from project.classifiers.linear_classifier import Softmax

    X_train, y_train, X_val, y_val = _load_cifar_small()

    N_train = X_train.shape[0]
    N_val = X_val.shape[0]

    # Raw pixel features.
    X_train_raw = X_train.reshape(N_train, -1)
    X_val_raw = X_val.reshape(N_val, -1)

    # HOG + color histogram features.
    X_train_feat = extract_features(X_train, [hog_feature, color_histogram_hsv])
    X_val_feat = extract_features(X_val, [hog_feature, color_histogram_hsv])

    def train_and_eval(Xtr, ytr, Xva, yva):
        clf = Softmax()
        clf.train(
            Xtr,
            ytr,
            learning_rate=1e-7,
            reg=2.5e4,
            num_iters=400,
            batch_size=200,
        )
        y_pred = clf.predict(Xva)
        return np.mean(y_pred == yva)

    acc_raw = train_and_eval(X_train_raw, y_train, X_val_raw, y_val)
    acc_feat = train_and_eval(X_train_feat, y_train, X_val_feat, y_val)

    # On CIFAR-10 subset, both pipelines should be noticeably better than random
    # guessing (10%), and the feature pipeline should at least not collapse.
    assert acc_raw >= 0.15
    assert acc_feat >= 0.12
