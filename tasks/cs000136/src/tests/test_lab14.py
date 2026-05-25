import os
import numpy as np
import pandas as pd
import pytest
import tensorflow as tf

import lab14 as st


# ---------------------------
# Reference helpers (for comparisons)
# ---------------------------

def _ref_softmax_model(input_dim, num_classes, l2=4e-4):
    m = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_dim,)),
        tf.keras.layers.Dense(
            num_classes,
            activation=None,
            kernel_regularizer=tf.keras.regularizers.l2(l2),
        ),
    ])
    m.compile(
        optimizer=tf.keras.optimizers.SGD(learning_rate=1.0),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy(name="acc")],
    )
    return m


def _ref_confusion_matrix(preds, truths, C):
    M = np.zeros((C, C), dtype=float)
    for i in range(C):
        idx = (truths == i)
        n = idx.sum()
        if n > 0:
            counts = np.bincount(preds[idx], minlength=C).astype(float)
            M[i, :] = counts / n
    return M


# ---------------------------
# Fixtures
# ---------------------------

@pytest.fixture(scope="module")
def toy_data():
    Xtr, ytr, Xte, yte = st.make_blobs(
        n_per_class=2000,
        num_classes=5,
        dim=64,
        sep=10.0,
        seed=42,
    )
    # validation split from train
    Xtr, Xva = Xtr[:800], Xtr[800:]
    ytr, yva = ytr[:800], ytr[800:]
    return Xtr, ytr, Xva, yva, Xte, yte


# ---------------------------
# Tests: seeds & datasets
# ---------------------------

def test_set_global_seed_reproducible():
    try:
        st.set_global_seed(123)
    except NotImplementedError:
        raise
    a1 = np.random.standard_normal(5)
    t1 = tf.random.uniform((4,), dtype=tf.float32)
    st.set_global_seed(123)
    a2 = np.random.standard_normal(5)
    t2 = tf.random.uniform((4,), dtype=tf.float32)
    assert np.allclose(a1, a2)
    assert np.allclose(t1.numpy(), t2.numpy(), atol=1e-7)


def test_make_tf_dataset_shapes(toy_data):
    Xtr, ytr, *_ = toy_data
    try:
        ds = st.make_tf_dataset(Xtr, ytr, batch_size=64, shuffle=True, seed=0)
    except NotImplementedError:
        raise
    xb, yb = next(iter(ds))
    assert xb.shape[1] == Xtr.shape[1]
    assert yb.ndim == 1

    ds2 = st.make_tf_dataset(Xtr, None, batch_size=32, shuffle=False)
    xb2 = next(iter(ds2))
    assert isinstance(xb2, tf.Tensor)
    assert xb2.shape[1] == Xtr.shape[1]


def test_make_tf_dataset_shuffle_repro(toy_data):
    Xtr, ytr, *_ = toy_data
    try:
        ds1 = st.make_tf_dataset(Xtr, ytr, batch_size=64, shuffle=True, seed=123)
        ds2 = st.make_tf_dataset(Xtr, ytr, batch_size=64, shuffle=True, seed=123)
    except NotImplementedError:
        raise

    X1 = np.concatenate([b[0].numpy() for b in ds1], axis=0)
    X2 = np.concatenate([b[0].numpy() for b in ds2], axis=0)
    assert np.array_equal(X1, X2)

    ds3 = st.make_tf_dataset(Xtr, ytr, batch_size=64, shuffle=True, seed=456)
    X3 = np.concatenate([b[0].numpy() for b in ds3], axis=0)
    # extremely unlikely to be identical with a different seed
    assert not np.array_equal(X1, X3)

    ds4 = st.make_tf_dataset(Xtr, ytr, batch_size=64, shuffle=False)
    X4 = np.concatenate([b[0].numpy() for b in ds4], axis=0)
    assert np.array_equal(X4, Xtr)


# ---------------------------
# Tests: compile & predict
# ---------------------------

def test_compile_classifier_uses_sgd(toy_data):
    Xtr, ytr, *_ = toy_data
    model = st.build_softmax_regression(Xtr.shape[1], num_classes=5, l2=1e-4)
    st.compile_classifier(model, lr=0.5)
    assert isinstance(model.optimizer, tf.keras.optimizers.SGD)
    assert isinstance(model.loss, tf.keras.losses.SparseCategoricalCrossentropy)
    assert model.loss.from_logits is True


def test_predict_classes_indices(toy_data):
    Xtr, ytr, Xva, yva, Xte, yte = toy_data
    try:
        model = st.build_softmax_regression(Xtr.shape[1], num_classes=5, l2=1e-4)
        st.compile_classifier(model, lr=1.0)
        st.train_softmax_regression(
            model,
            Xtr,
            ytr,
            Xva,
            yva,
            epochs=10,
            patience=3,
            batch_size=64,
            verbose=0,
        )
        preds = st.predict_classes(model, Xte, batch_size=128)
    except NotImplementedError:
        raise

    assert preds.shape == (Xte.shape[0],)
    assert preds.dtype.kind in "iu"
    assert preds.min() >= 0 and preds.max() <= 4


# ---------------------------
# Tests: confusion matrix
# ---------------------------

def test_confusion_matrix_basic(toy_data):
    Xtr, ytr, Xva, yva, Xte, yte = toy_data
    try:
        model = st.build_softmax_regression(Xtr.shape[1], num_classes=5, l2=1e-4)
        st.compile_classifier(model, lr=1.0)
        st.train_softmax_regression(
            model,
            Xtr,
            ytr,
            Xva,
            yva,
            epochs=5,
            patience=2,
            batch_size=64,
            verbose=0,
        )
        preds = st.predict_classes(model, Xte, batch_size=256)
        M = st.compute_confusion_matrix(preds, yte, num_classes=5)
    except NotImplementedError:
        raise

    M_ref = _ref_confusion_matrix(preds, yte, 5)
    assert M.shape == (5, 5)
    row_sums = M.sum(axis=1)
    mask = row_sums > 0
    assert np.allclose(row_sums[mask], 1.0, atol=1e-6)
    assert np.allclose(M, M_ref, atol=1e-6)


def test_confusion_matrix_handles_missing_class():
    preds = np.array([0, 0, 1, 1], dtype=int)
    truths = np.array([0, 0, 0, 1], dtype=int)  # class 2 never appears
    M = st.compute_confusion_matrix(preds, truths, num_classes=3)
    M_ref = _ref_confusion_matrix(preds, truths, 3)
    assert M.shape == (3, 3)
    assert np.allclose(M, M_ref, atol=1e-8)
    # row for class 2 should be all zeros
    assert np.allclose(M[2, :], 0.0)


# ---------------------------
# Tests: training — softmax regression
# ---------------------------

def test_softmax_regression_trains_on_blobs(toy_data):
    Xtr, ytr, Xva, yva, Xte, yte = toy_data
    st.set_global_seed(0)

    model = st.build_softmax_regression(Xtr.shape[1], num_classes=5, l2=1e-4)
    st.compile_classifier(model, lr=1.0)
    hist = st.train_softmax_regression(
        model,
        Xtr,
        ytr,
        Xva,
        yva,
        epochs=25,
        patience=5,
        batch_size=64,
        verbose=0,
    )

    assert isinstance(hist, tf.keras.callbacks.History)
    preds = st.predict_classes(model, Xte, batch_size=256)
    acc = float(np.mean(preds == yte))
    assert acc >= 0.90


# ---------------------------
# Tests: Max-of-K filters model
# ---------------------------

def test_build_max_of_k_filters_output_shape(toy_data):
    Xtr, ytr, *_ = toy_data
    num_classes = 5
    k = 3
    try:
        model = st.build_max_of_k_filters_model(
            input_dim=Xtr.shape[1],
            num_classes=num_classes,
            k=k,
            l2=1e-6,
        )
    except NotImplementedError:
        raise

    x_dummy = tf.zeros((4, Xtr.shape[1]), dtype=tf.float32)
    y_dummy = model(x_dummy)
    assert y_dummy.shape == (4, num_classes)

    dense_layers = [l for l in model.layers if isinstance(l, tf.keras.layers.Dense)]
    assert len(dense_layers) >= 1
    assert dense_layers[0].units == num_classes * k


def test_train_model_generic_trains_max_of_k(toy_data):
    Xtr, ytr, Xva, yva, Xte, yte = toy_data
    st.set_global_seed(0)
    num_classes = 5
    k = 2

    try:
        model = st.build_max_of_k_filters_model(
            input_dim=Xtr.shape[1],
            num_classes=num_classes,
            k=k,
            l2=1e-6,
        )
        hist = st.train_model_generic(
            model,
            X_train=Xtr,
            y_train=ytr,
            X_val=Xva,
            y_val=yva,
            epochs=25,
            patience=5,
            batch_size=64,
            lr=1.0,
            verbose=0,
        )
    except NotImplementedError:
        raise

    assert isinstance(hist, tf.keras.callbacks.History)
    assert isinstance(model.optimizer, tf.keras.optimizers.SGD)
    assert isinstance(model.loss, tf.keras.losses.SparseCategoricalCrossentropy)
    assert model.loss.from_logits is True

    preds = st.predict_classes(model, Xte, batch_size=256)
    acc = float(np.mean(preds == yte))
    assert acc >= 0.92


# ---------------------------
# Tests: optional helpers
# ---------------------------

def test_load_local_mnist_npz_missing_ok():
    # use a filename that should not exist
    data = st.load_local_mnist_npz("this_file_does_not_exist_mnist.npz")
    assert data is None


def test_load_optional_csv_missing_ok():
    df = st.load_optional_csv("this_file_does_not_exist_lab14_extra.csv")
    assert df is None


@pytest.mark.skipif(
    not os.path.exists("mnist.npz"),
    reason="mnist.npz not found in working directory",
)
def test_mnist_short_run_optional():
    data = st.load_local_mnist_npz("mnist.npz")
    if data is None:
        raise

    if isinstance(data, dict):
        Xtr = data["x_train"]
        ytr = data["y_train"]
        Xte = data["x_test"]
        yte = data["y_test"]
    else:
        Xtr, ytr, Xte, yte = data

    Xtr = Xtr.reshape((Xtr.shape[0], -1)).astype("float32")
    Xte = Xte.reshape((Xte.shape[0], -1)).astype("float32")

    # small subset for speed
    X_train = Xtr[:2000]
    y_train = ytr[:2000]
    X_val = Xtr[2000:2500]
    y_val = ytr[2000:2500]
    X_test = Xte[:1000]
    y_test = yte[:1000]

    st.set_global_seed(0)
    model = st.build_max_of_k_filters_model(
        input_dim=X_train.shape[1],
        num_classes=10,
        k=2,
        l2=1e-6,
    )
    st.train_model_generic(
        model,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        epochs=10,
        patience=3,
        batch_size=128,
        lr=0.1,
        verbose=0,
    )
    preds = st.predict_classes(model, X_test, batch_size=256)
    acc = float(np.mean(preds == y_test))
    assert acc >= 0.90