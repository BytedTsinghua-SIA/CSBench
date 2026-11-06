from pathlib import Path
import sys

import numpy as np


def _ensure_project_root_on_path():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def test_linear_classifier_benefits_from_features_on_synthetic_data():
    _ensure_project_root_on_path()
    from project.features import extract_features, hog_feature, color_histogram_hsv
    from project.classifiers.linear_classifier import Softmax

    np.random.seed(0)
    N_per_class = 20
    C = 3
    D_img = 8
    imgs = []
    labels = []
    for c in range(C):
        base = np.zeros((D_img, D_img, 3), dtype=np.float64)
        base[:, :, c % 3] = 50 + 50 * c
        for _ in range(N_per_class):
            noise = 5 * np.random.randn(D_img, D_img, 3)
            imgs.append(base + noise)
            labels.append(c)
    imgs = np.stack(imgs, axis=0)
    labels = np.array(labels, dtype=np.int64)

    raw_X = imgs.reshape(imgs.shape[0], -1)
    feat_X = extract_features(imgs, [hog_feature, color_histogram_hsv])

    def train_and_eval(X):
        num_train = int(0.7 * X.shape[0])
        X_train, y_train = X[:num_train], labels[:num_train]
        X_val, y_val = X[num_train:], labels[num_train:]
        clf = Softmax()
        clf.train(X_train, y_train, learning_rate=1e-7, reg=1e-3, num_iters=50, batch_size=10)
        y_pred = clf.predict(X_val)
        return np.mean(y_pred == y_val)

    acc_raw = train_and_eval(raw_X)
    acc_feat = train_and_eval(feat_X)

    assert acc_feat >= acc_raw
