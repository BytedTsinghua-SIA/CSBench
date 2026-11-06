import numpy as np
from decision_tree_starter import (
    BaggedTrees,
    BoostedRandomForest,
    DecisionTree,
    preprocess,
    RandomForest,
)


def test_information_gain_perfect_split():
    X = np.array([0.0, 0.0, 1.0, 1.0])
    y = np.array([0, 0, 1, 1])
    gain = DecisionTree.information_gain(X, y, 0.5)
    assert np.isclose(gain, 1.0, atol=1e-4)


def test_information_gain_handles_empty_split():
    X = np.array([1.0, 1.0, 1.0])
    y = np.array([0, 1, 1])
    gain = DecisionTree.information_gain(X, y, 0.0)
    assert gain == 0.0


def test_gini_impurity_weighted_average():
    X = np.array([0.0, 0.0, 1.0, 1.0])
    y = np.array([0, 0, 1, 1])
    gini = DecisionTree.gini_impurity(X, y, 0.5)
    assert np.isclose(gini, 0.0)


def test_preprocess_onehot_and_mode_imputation():
    raw = np.array(
        [
            ["red", "1", "10"],
            ["red", "1", "12"],
            ["blue", "2", "12"],
            ["red", "", "12"],
        ],
        dtype=object,
    )
    processed, features = preprocess(raw.copy(), fill_mode=True, min_freq=1, onehot_cols=[0])
    assert features == ["red"]
    assert processed.shape == (4, 4)
    # Original categorical column is zeroed and the one-hot column reflects frequent categories.
    np.testing.assert_array_equal(processed[:, 0], np.zeros(4))
    np.testing.assert_array_equal(processed[:, -1], np.array([1.0, 1.0, 0.0, 1.0]))
    # Missing values are replaced by the mode when fill_mode is enabled.
    assert not np.any(np.isclose(processed, -1.0))
    assert processed[3, 1] == 1.0


def test_preprocess_respects_min_freq_and_fill_mode_flag():
    raw = np.array(
        [
            ["cat", "5"],
            ["dog", ""],
            ["dog", "6"],
            ["cat", "7"],
        ],
        dtype=object,
    )
    processed, features = preprocess(raw.copy(), fill_mode=False, min_freq=2, onehot_cols=[0])
    assert features == []
    assert processed.shape == (4, 2)
    np.testing.assert_array_equal(processed[:, 0], np.zeros(4))
    # Missing values stay as the sentinel when fill_mode is False.
    assert processed[1, 1] == -1.0


def test_decision_tree_best_split_prefers_informative_feature_depth1():
    X = np.array(
        [
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 2.0],
            [1.0, 2.0],
        ]
    )
    y = np.array([0, 1, 0, 1, 1, 1])
    tree = DecisionTree(max_depth=1)
    tree.fit(X, y)
    preds = tree.predict(X)
    assert np.array_equal(preds, y)


def test_decision_tree_no_valid_split_predicts_majority():
    X = np.zeros((7, 2), dtype=float)
    y = np.array([1, 1, 1, 1, 0, 1, 0])
    tree = DecisionTree(max_depth=3)
    tree.fit(X, y)
    preds = tree.predict(X)
    assert preds.shape == y.shape
    assert np.all(preds == 1)


def test_bagged_trees_bootstrap_predicts_training_data():
    X = np.array([[0.0], [0.0], [1.0], [1.0]])
    y = np.array([0, 0, 1, 1])
    model = BaggedTrees(params={"max_depth": 1}, n=5)
    model.fit(X, y)
    preds = model.predict(X)
    assert np.array_equal(preds, y)


def test_random_forest_sets_max_features():
    forest = RandomForest(params={"max_depth": 2}, n=3, m=2)
    assert all(tree.max_features == 2 for tree in forest.decision_trees)


def test_boosted_random_forest_learns_weights():
    X = np.array([[0.0], [0.0], [1.0], [1.0]])
    y = np.array([0, 0, 1, 1])
    model = BoostedRandomForest(params={"max_depth": 1}, n=3, m=1)
    model.fit(X, y)
    preds = model.predict(X)
    assert np.array_equal(preds, y)
    assert np.any(model.a != 0)
