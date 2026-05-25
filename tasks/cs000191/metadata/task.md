## 任务说明

### 任务来源

EECS 498-007 / 598-005
Deep Learning for Computer Vision

### 任务概述

1. edit `knn.py` to implement the k-Nearest Neighbor classifier.
2. edit `pytorch101.py` to complete basic tensor operations in PyTorch.

In this assignment, you will first learn how to use PyTorch on Google Colab environment. You will then practice putting together a simple image classification pipeline, based on the k-Nearest Neighbor, and finally will learn how to use Autograder for evaluating what you implement. The goals of this assignment are as follows:

- Develop proficiency with PyTorch tensors
- Gain experience using notebooks on Google Colab
- Understand the basic Image Classification pipeline and the data-driven approach (train/predict stages)
- Understand the train/val/test splits and the use of validation data for hyperparameter tuning
- Implement and apply a k-Nearest Neighbor (kNN) classifier
- Learn how to test your implementation on Autograder

### 详细要求

TODO: 参考 knn.py 和 pytorch101.py 中函数的doc 描述详细要求

1. In `pytorch101.py`, implement the following functions:
   - `create_sample_tensor`
   - `mutate_tensor`
   - `count_tensor_elements`
   - `create_tensor_of_pi`
   - `multiples_of_ten`
   - `slice_indexing_practice`
   - `slice_assignment_practice`
   - `shuffle_cols`
   - `reverse_rows`
   - `take_one_elem_per_col`
   - `make_one_hot`
   - `sum_positive_entries`
   - `reshape_practice`
   - `zero_row_min`
   - `batched_matrix_multiply`
   - `batched_matrix_multiply_loop`
   - `batched_matrix_multiply_noloop`
   - `normalize_columns`
   - `mm_on_cpu`
   - `mm_on_gpu`
   - `challenge_mean_tensors`
   - `challenge_get_uniques`

    The detailed description of each function can be found in the docstring of each function in `pytorch101.py`.

2. In `knn.py`, implement the following functions:
    - `compute_distances_two_loops`
    - `compute_distances_one_loop`
    - `compute_distances_no_loops`
    - `predict_labels`
    - class `KnnClassifier`
    - `knn_cross_validate`
    - `knn_get_best_k`

    The detailed description of each function can be found in the docstring of each function in `knn.py`.