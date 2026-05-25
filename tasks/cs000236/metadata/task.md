## Background (Excerpts from the Assignment 1 handout)

This assignment focuses on building a simple image classification pipeline using classic, data-driven methods. You will implement and compare multiple classifiers and representation choices through a set of Colab notebooks.

Outcomes you will gain from this assignment include:

- Understanding the basic Image Classification pipeline and the data-driven approach (train/predict stages).
- Understanding train/val/test splits and the use of validation data for hyperparameter tuning.
- Developing proficiency in writing efficient, vectorized code with numpy.
- Implementing and applying multiple classifiers (kNN, Softmax, two-layer neural network, fully connected network).
- Understanding differences and tradeoffs between these classifiers.
- Understanding performance improvements from higher-level representations versus raw pixels (e.g., color histograms, HOG features).

### Q1: k-Nearest Neighbor classifier

Goal: implement and evaluate a kNN image classifier on CIFAR-10 using only Python code.

Conceptual background (from the original notebook):

- During training, the classifier stores all training images and labels.
- During testing, it compares each test image to all training images, finds the k most similar training examples, and lets them vote for the label.
- The value of k is selected by cross-validation.

Code to edit:

- `project/classifiers/k_nearest_neighbor.py`: implement the methods
  - `compute_distances_two_loops`
  - `compute_distances_one_loop`
  - `compute_distances_no_loops`
  - `predict_labels`
- In your own driver code (or an interactive session), you should also
-  - load CIFAR-10 using `project.data_utils.load_CIFAR10`;
  - subsample the data for speed;
  - perform k-fold cross-validation over a list of k values using `np.array_split`;
  - train a final model on all training data with the best k and evaluate on the test set.

### Q2: Implement a Softmax classifier

Goal: train a linear classifier with Softmax loss on CIFAR-10.

Conceptual background (from the original notebook):

- Implement a fully vectorized Softmax loss function.
- Implement the analytic gradient of the Softmax loss.
- Check your implementation with numerical gradients.
- Use a validation set to tune learning rate and regularization.
- Optimize the loss with stochastic gradient descent (SGD).
- Visualize the learned weight vectors as images.

Code to edit:

- `project/classifiers/softmax.py`:
  - In `softmax_loss_naive`, compute the gradient `dW` while you compute the loss.
  - In `softmax_loss_vectorized`, implement both the vectorized loss and gradient.
- `project/classifiers/linear_classifier.py`:
  - In `LinearClassifier.train`, sample minibatches from `(X, y)` using `np.random.choice`,
    call `self.loss`, and update `self.W` using the returned gradient.
  - In `LinearClassifier.predict`, compute class scores and return the predicted labels.

You can write a small Python script that:

- loads CIFAR-10;
- reshapes images into rows;
- trains a `LinearSVM` and `Softmax` model with different hyperparameters;
- evaluates on validation and test sets.

### Q3: Two-Layer Neural Network

Goal: implement and train a simple fully connected network with one hidden layer
and ReLU nonlinearity.

Conceptual background (from the original notebook):

- Use a modular design where each layer has a forward function that returns
  both outputs and a cache, and a backward function that receives upstream
  derivatives and the cache to compute gradients.
- Combine affine layers, ReLU, and a softmax loss into an architecture
  `affine -> ReLU -> affine -> softmax`.

Code to edit:

- `project/classifiers/fc_net.py` (class `TwoLayerNet`):
  - In `__init__`, initialize `W1`, `b1`, `W2`, `b2` in `self.params` using
    Gaussian weights with standard deviation `weight_scale` and zero biases.
  - In `loss`, implement the forward pass to compute class scores, and the
    backward pass to compute gradients and softmax loss with L2 regularization.

You can then construct a `TwoLayerNet`, wrap it in the `project.solver.Solver`
class, and train it on CIFAR-10.

### Q4: Higher Level Representations: Image Features

Goal: compare linear classifiers trained on raw pixels versus higher-level features.

Conceptual background (from the original notebook):

- Training on raw pixels can work but often underperforms.
- Hand-crafted features such as Histogram of Oriented Gradients (HOG) and
  color histograms can significantly improve linear classifier performance.

Code to use:

- `project/features.py`:
  - `extract_features` to turn a batch of images into feature vectors.
  - `hog_feature` to compute HOG descriptors.
  - `color_histogram_hsv` to compute color histograms.

Typical experiment flow:

- Load CIFAR-10 images.
- Build raw-pixel features and train a linear classifier.
- Build HOG + color histogram features and train a linear classifier.
- Compare validation/test accuracy between feature choices.

### Q5: Training a fully connected network

Goal: implement and train a deeper fully connected network with optional
dropout and (batch or layer) normalization.

Conceptual background (from the original notebook):

- Implement a `FullyConnectedNet` class that supports an arbitrary number of
  hidden layers with ReLU, optional dropout, and optional normalization.
- Reuse the modular layers from `project/layers.py` and composition utilities
-  from `project/layer_utils.py`.
- Explore the effect of depth, regularization, learning rate schedules, and
  different update rules on CIFAR-10 performance.

Code to edit:

- `project/classifiers/fc_net.py` (class `FullyConnectedNet`):
  - Initialize parameters for all layers in `__init__` (weights `W1...WL`,
    biases `b1...bL`, and optional `gamma`/`beta` for normalization).
  - Implement the full forward and backward passes in `loss`, including
    dropout and batch/layer normalization when requested.
- `project/layers.py`:
  - Implement `layernorm_forward` and `layernorm_backward`.
  - Implement `dropout_forward` and `dropout_backward` (inverted dropout).
- `project/optim.py`:
  - Implement `sgd_momentum`, `rmsprop`, and `adam` update rules.

Once these pieces are in place, you can use `project.solver.Solver` to train
deep networks on CIFAR-10 and run the experiments that were previously done
inside the Colab notebooks.

---

## Special reminders for this repository

- This repo is intended to be used without Colab or Google Drive; you work
-  directly with the Python files under `project/`.
- The original notebooks are only a reference for text and plots; students
  should complete all TODOs in the `.py` files instead of editing notebooks.
