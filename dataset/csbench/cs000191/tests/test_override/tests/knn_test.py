import torch
import pytest
from ..knn import *


class TestKnn:
    def test_compute_distances_variants(self):
        # Small synthetic dataset
        x_train = torch.tensor([[0.0, 0.0], [1.0, 1.0], [2.0, 0.0]])
        x_test = torch.tensor([[0.0, 0.0], [1.0, 0.0], [2.0, 2.0]])

        d_two = compute_distances_two_loops(x_train, x_test)
        d_one = compute_distances_one_loop(x_train, x_test)
        d_no = compute_distances_no_loops(x_train, x_test)

        # Shapes and dtype
        assert d_two.shape == (x_train.shape[0], x_test.shape[0])
        assert d_one.shape == d_two.shape
        assert d_no.shape == d_two.shape
        assert d_two.dtype == x_train.dtype

        # All implementations should agree
        assert torch.allclose(d_two, d_one)
        assert torch.allclose(d_two, d_no)

        # Distances should be >= 0 and zero for identical vectors
        assert torch.all(d_two >= 0)
        assert d_two[0, 0] == 0

    def test_predict_labels_and_tie_breaking(self):
        # Build a distances matrix for 4 training points and 2 test points
        # Column 0: nearest labels tie between 1 and 2 when k=4
        dists = torch.tensor([
            [0.0, 10.0],
            [1.0, 0.1],
            [2.0, 20.0],
            [3.0, 30.0]
        ])
        y_train = torch.tensor([1, 2, 1, 2], dtype=torch.int64)

        # k=1 should pick the nearest neighbor
        y_pred_k1 = predict_labels(dists, y_train, k=1)
        assert y_pred_k1.shape == (2,)
        assert y_pred_k1[0].item() == 1  # nearest for test 0 is train 0

        # k=4 produces a tie between 1 and 2 for test 0: expect smaller label (1)
        y_pred_k4 = predict_labels(dists, y_train, k=4)
        assert y_pred_k4[0].item() == 1

        # Test 1 should pick label 2 for k=1
        assert y_pred_k1[1].item() == 2

    def test_knnclassifier_predict_and_check_accuracy(self):
        # Simple 1D points, labels 0/1
        x_train = torch.tensor([[0.0], [1.0], [2.0]])
        y_train = torch.tensor([0, 1, 1], dtype=torch.int64)

        clf = KnnClassifier(x_train, y_train)

        x_test = torch.tensor([[0.1], [1.9]])
        y_test = torch.tensor([0, 1], dtype=torch.int64)

        y_pred = clf.predict(x_test, k=1)
        assert torch.allclose(y_pred.to(torch.float32), y_test.to(torch.float32))

        acc = clf.check_accuracy(x_test, y_test, k=1, quiet=True)
        assert isinstance(acc, float)
        assert abs(acc - 100.0) < 1e-8

    def test_knn_cross_validate_and_get_best_k_structure(self):
        # Construct a dataset with clear clusters: three zeros then three ones
        x_train = torch.tensor([[0.0], [0.0], [0.0], [1.0], [1.0], [1.0]])
        y_train = torch.tensor([0, 0, 0, 1, 1, 1], dtype=torch.int64)

        k_choices = [1, 3]
        results = knn_cross_validate(x_train, y_train, num_folds=3, k_choices=k_choices)

        # Results should be a dict with an entry for each k and each entry a list of length num_folds
        assert set(results.keys()) == set(k_choices)
        for accs in results.values():
            assert isinstance(accs, list)
            assert len(accs) == 3
            for a in accs:
                assert isinstance(a, float)
                assert 0.0 <= a <= 100.0

        best = knn_get_best_k(results)
        assert best in k_choices

    def test_knn_get_best_k_tie_returns_smallest(self):
        k_to_accuracies = {
            1: [90.0, 90.0],
            3: [90.0, 90.0],
            5: [80.0, 80.0]
        }
        best = knn_get_best_k(k_to_accuracies)
        assert best == 1


if __name__ == "__main__":
    pytest.main([__file__])
