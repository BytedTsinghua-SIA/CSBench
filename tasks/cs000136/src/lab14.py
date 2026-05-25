# Lab 14: Deep(er) MNIST with TensorFlow — Student Version
# Importing this file must not run training or heavy I/O.
# Only calling TODO-marked functions should raise NotImplementedError.

from __future__ import annotations
from typing import Tuple, Optional, Sequence
import os
import math
import random
import numpy as np
import pandas as pd
import tensorflow as tf


# ---------------------------
# Reproducibility
# ---------------------------

def set_global_seed(seed: int = 0) -> None:
    """
    Set global seeds for Python, NumPy, and TensorFlow.

    TODO: set seeds for random, numpy, and tf.
    """
    raise NotImplementedError


# ---------------------------
# Data utilities (no downloads)
# ---------------------------

def load_local_mnist_npz(path: str = "mnist.npz") -> Optional[Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]]:
    """
    Load MNIST from a local 'mnist.npz' if present. Returns ((x_train, y_train), (x_test, y_test))
    with x as float32 in [0,1] and y as int64 labels (0..9). If file is missing, return None.
    """
    if not os.path.exists(path):
        return None
    with np.load(path) as f:
        x_train, y_train = f["x_train"], f["y_train"]
        x_test, y_test = f["x_test"], f["y_test"]
    x_train = (x_train.reshape((-1, 28 * 28)).astype("float32")) / 255.0
    x_test = (x_test.reshape((-1, 28 * 28)).astype("float32")) / 255.0
    y_train = y_train.astype(np.int64)
    y_test = y_test.astype(np.int64)
    return (x_train, y_train), (x_test, y_test)


def load_optional_csv(path: str = "lab14_extra.csv") -> Optional[pd.DataFrame]:
    """
    If a CSV at `path` exists, load and return it; else return None.
    Expected columns: feature columns (float) and a 'target' integer label.
    """
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


def make_blobs(
    n_per_class: int = 400,
    num_classes: int = 10,
    dim: int = 28 * 28,
    sep: float = 5.0,
    seed: int = 0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Create a synthetic MNIST-like classification task with Gaussian blobs in a subspace,
    then embed to `dim`. Returns train/test splits (Xtr, ytr, Xte, yte).
    """
    rng = np.random.default_rng(seed)
    centers = rng.standard_normal((num_classes, 16))
    centers = centers / (np.linalg.norm(centers, axis=1, keepdims=True) + 1e-8) * sep
    def samp(n):
        z = rng.standard_normal((n * num_classes, 16))
        y = np.repeat(np.arange(num_classes), n)
        mu = np.repeat(centers, n, axis=0)
        z = z + mu
        P = rng.standard_normal((16, dim))
        x = z @ P
        x = (x - x.min()) / (x.max() - x.min() + 1e-8)
        return x.astype(np.float32), y.astype(np.int64)
    Xtr, ytr = samp(n_per_class)
    Xte, yte = samp(max(50, n_per_class // 4))
    return Xtr, ytr, Xte, yte


# ---------------------------
# Dataset wrappers
# ---------------------------

def make_tf_dataset(
    X: np.ndarray,
    y: Optional[np.ndarray] = None,
    batch_size: int = 128,
    shuffle: bool = True,
    seed: int = 0,
) -> tf.data.Dataset:
    """
    Wrap arrays into a tf.data.Dataset.

    TODO:
      - If y is None: return Dataset of X only.
      - Else: return Dataset of (X, y).
      - Apply shuffle if requested (buffer size = len(X)), then batch.
    """
    raise NotImplementedError


# ---------------------------
# Models: (1) Softmax regression (logistic regression over 10 classes)
# ---------------------------

def build_softmax_regression(
    input_dim: int,
    num_classes: int,
    l2: float = 4e-4,
) -> tf.keras.Model:
    """
    Build a single-layer softmax regression model that outputs logits.

    TODO:
      - Use tf.keras.Sequential with Input(shape=(input_dim,))
      - Dense(num_classes, activation=None, kernel_regularizer=tf.keras.regularizers.l2(l2))
    """
    raise NotImplementedError


def compile_classifier(
    model: tf.keras.Model,
    lr: float = 1.0,
) -> None:
    """
    Compile with SGD(lr), SparseCategoricalCrossentropy(from_logits=True), and SparseCategoricalAccuracy.

    TODO: compile in-place.
    """
    raise NotImplementedError


def train_softmax_regression(
    model: tf.keras.Model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    batch_size: int = 128,
    epochs: int = 10,
    patience: int = 3,
    seed: int = 0,
) -> tf.keras.callbacks.History:
    """
    Train with EarlyStopping on val_loss (restore_best_weights=True). Return History.

    TODO:
      - Build train/val datasets with make_tf_dataset
      - Fit model with the early stopping callback
    """
    raise NotImplementedError


def predict_classes(
    model: tf.keras.Model,
    X: np.ndarray,
    batch_size: int = 256,
) -> np.ndarray:
    """
    Return predicted class indices from logits.

    TODO:
      - Call model.predict to obtain logits
      - Take argmax over axis=1 to produce integer labels
    """
    raise NotImplementedError


# ---------------------------
# Models: (2) Max-of-K filters per class (shallow but more expressive)
# ---------------------------

def build_max_of_k_filters_model(
    input_dim: int,
    num_classes: int,
    k: int = 2,
    l2: float = 1e-6,
) -> tf.keras.Model:
    """
    Build a linear model with K filters per class and max-reduction across filters.
    This mimics 'take the max score across K templates for each class'.

    Architecture (Functional API):
      Input -> Dense(num_classes*k, activation=None, kernel_regularizer=l2)
            -> Reshape((num_classes, k))
            -> ReduceMax(axis=2)  # logits per class

    TODO: implement the model and return it (uncompiled).
    """
    raise NotImplementedError


def train_model_generic(
    model: tf.keras.Model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    lr: float = 2.0,
    batch_size: int = 128,
    epochs: int = 30,
    patience: int = 5,
) -> tf.keras.callbacks.History:
    """
    Generic trainer for any classifier with logits output.

    TODO:
      - Compile with SGD(lr), SparseCategoricalCrossentropy(from_logits=True), accuracy metric
      - Use EarlyStopping on val_loss with restore_best_weights=True
    """
    raise NotImplementedError


# ---------------------------
# Metrics
# ---------------------------

def compute_confusion_matrix(
    classifications: np.ndarray,
    true_classes: np.ndarray,
    num_classes: int,
) -> np.ndarray:
    """
    Compute confusion matrix where element [i, j] is the proportion of examples
    with true class i that were assigned class j.

    TODO:
      - For each true class i, compute distribution of predicted classes
      - Normalize each row to sum to 1 (if row has no samples, keep zeros)
    """
    raise NotImplementedError