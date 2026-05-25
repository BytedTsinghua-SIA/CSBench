# Lab 14 — From Softmax Regression to “Max-of-K” Filters (TensorFlow)

## Objective
Recreate a simplified MNIST classification pipeline using TensorFlow/Keras:
1) a baseline **softmax regression** classifier, and 2) a shallow but more expressive classifier with **K linear filters per class** combined by a max-reduction (“match any of K templates”). You will also implement a **confusion matrix** utility.

## What to implement (in `lab14.py`)
- **Reproducibility**
  - `set_global_seed(seed)`: set seeds for `random`, `numpy`, and `tensorflow`.

- **Dataset wrapper**
  - `make_tf_dataset(X, y=None, batch_size=128, shuffle=True, seed=0)`: return a `tf.data.Dataset`. If `y` is `None`, yield only `X`; otherwise yield `(X, y)`. Apply optional shuffle (buffer = `len(X)`) then batch.

- **Softmax regression**
  - `build_softmax_regression(input_dim, num_classes, l2=4e-4)`: Single `Dense(num_classes)` (logits) with L2 regularization.
  - `compile_classifier(model, lr=1.0)`: SGD optimizer, `SparseCategoricalCrossentropy(from_logits=True)`, accuracy metric.
  - `train_softmax_regression(model, X_train, y_train, X_val, y_val, ...)`: Train with `EarlyStopping` on `val_loss`, `restore_best_weights=True`. Return `History`.
  - `predict_classes(model, X, ...)`: Run inference and return `argmax` class indices.

- **Max-of-K filters (per class)**
  - `build_max_of_k_filters_model(input_dim, num_classes, k=2, l2=1e-6)`: Dense layer with `num_classes * k` logits → `Reshape((num_classes, k))` → `ReduceMax(axis=2)` to obtain per-class logits.
  - `train_model_generic(model, X_train, y_train, X_val, y_val, ...)`: Generic trainer (SGD + cross-entropy + accuracy) with early stopping.

- **Metrics**
  - `compute_confusion_matrix(classifications, true_classes, num_classes)`: Return a matrix where element `[i, j]` is the **proportion** of samples with true class `i` that were predicted as `j`.

## Provided helpers
- `load_local_mnist_npz("mnist.npz")`: If a local `mnist.npz` file is present in this folder, it loads and normalizes it; otherwise returns `None`.
- `load_optional_csv("lab14_extra.csv")`: If present, loads a CSV with float features and an integer `target`.
- `make_blobs(...)`: Generates a synthetic, linearly-separable multi-class dataset used by the tests (no downloads required).

## How we test (in `test_lab14.py`)
- Seed setting and `tf.data` behavior.
- Softmax model: build → compile → train to ≥0.90 accuracy on synthetic data.
- Max-of-K filters model: build → train to ≥0.92 accuracy on synthetic data.
- Predictions return valid integer class IDs.
- Confusion matrix equals a reference implementation.
- **Optional:** If `mnist.npz` is in the same directory, a short training run checks that test accuracy reaches ≥0.90.
