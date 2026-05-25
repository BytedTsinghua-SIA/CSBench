# Task Overview
Complete the decision tree and ensemble toolkit in `decision_tree_starter.py` for homework 5 while preserving the provided interfaces. Match the intended behavior for decision trees, bagging, random forests, boosting, and the shared preprocessing pipeline.

## Implementation Requirements
- DecisionTree: implement entropy-based `information_gain` that returns zero for empty branches, and weighted `gini_impurity` for 1-D threshold splits. The training routine should pick the split with the largest information gain over the provided threshold grid and populate leaf predictions with the modal label.
- BaggedTrees: train each `DecisionTreeClassifier` on a bootstrap sample of the input data and combine predictions by majority vote.
- RandomForest: reuse the bagging wrapper but configure every base tree with `max_features=m`, forwarding other hyperparameters and deterministic seeds.
- BoostedRandomForest: implement AdaBoost-style training that updates sample weights, records tree weights `a`, and aggregates signed votes for prediction.
- Preprocessing: keep every example and handle missing/categorical data explicitly. `preprocess` must treat empty strings as missing (`-1` sentinel), build one-hot vectors for each category in `onehot_cols` that appears more than `min_freq` times while skipping the sentinel, zero out the original categorical columns before casting to float and appending the one-hot columns, and when `fill_mode` is enabled replace every `-1` with the column mode computed after one-hot expansion.

## File Scope
Keep changes within `decision_tree_starter.py` and any supporting documentation or tests you add. Do not move or rename files, and keep the public interface intact. Hidden tests will be used during grading; do not rely on or reference any internal test paths.
