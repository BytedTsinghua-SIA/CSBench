import torch
import pytest
from typing import List, Tuple
from torch import Tensor
from ..pytorch101 import *

class TestPyTorch101:
    """Test suite for PyTorch 101 functions"""
    
    def test_hello(self, capsys):
        """Test hello function"""
        hello()
        captured = capsys.readouterr()
        assert captured.out.strip() == "Hello from pytorch101.py!"
    
    def test_create_sample_tensor(self):
        """Test create_sample_tensor function"""
        x = create_sample_tensor()
        assert x.shape == (3, 2)
        assert x[0, 1] == 10
        assert x[1, 0] == 100
        assert torch.all(x == torch.tensor([[0, 10], [100, 0], [0, 0]]))
    
    def test_mutate_tensor(self):
        """Test mutate_tensor function"""
        # Test basic mutation
        x = torch.zeros(3, 3)
        indices = [(0, 0), (1, 1), (2, 2)]
        values = [1.0, 2.0, 3.0]
        result = mutate_tensor(x, indices, values)
        assert result[0, 0] == 1.0
        assert result[1, 1] == 2.0
        assert result[2, 2] == 3.0
        
        # Test overwriting same index
        x = torch.zeros(2, 2)
        indices = [(0, 0), (0, 0), (1, 1)]
        values = [1.0, 5.0, 2.0]
        result = mutate_tensor(x, indices, values)
        assert result[0, 0] == 5.0  # Last value should be used
        assert result[1, 1] == 2.0
    
    def test_count_tensor_elements(self):
        """Test count_tensor_elements function"""
        # Test various shapes
        assert count_tensor_elements(torch.tensor([1, 2, 3])) == 3
        assert count_tensor_elements(torch.tensor([[1, 2], [3, 4]])) == 4
        assert count_tensor_elements(torch.tensor([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])) == 8
        assert count_tensor_elements(torch.tensor(5)) == 1  # Scalar tensor
    
    def test_create_tensor_of_pi(self):
        """Test create_tensor_of_pi function"""
        x = create_tensor_of_pi(2, 3)
        assert x.shape == (2, 3)
        assert torch.allclose(x, torch.full((2, 3), 3.14))
        
        x = create_tensor_of_pi(1, 1)
        assert x.shape == (1, 1)
        assert x[0, 0] == 3.14
    
    def test_multiples_of_ten(self):
        """Test multiples_of_ten function"""
        # Test normal range
        x = multiples_of_ten(0, 50)
        expected = torch.tensor([0.0, 10.0, 20.0, 30.0, 40.0, 50.0], dtype=torch.float64)
        assert torch.allclose(x, expected)
        
        # Test range with no multiples
        x = multiples_of_ten(1, 9)
        assert x.shape == (0,)
        assert x.dtype == torch.float64
        
        # Test single multiple
        x = multiples_of_ten(10, 10)
        assert x.shape == (1,)
        assert x[0] == 10.0
    
    def test_slice_indexing_practice(self):
        """Test slice_indexing_practice function"""
        x = torch.arange(20).reshape(4, 5)  # 4x5 tensor
        
        last_row, third_col, first_two_rows_three_cols, even_rows_odd_cols = slice_indexing_practice(x)
        
        # Test last_row
        assert last_row.shape == (5,)
        assert torch.allclose(last_row, x[-1, :])
        
        # Test third_col
        assert third_col.shape == (4, 1)
        assert torch.allclose(third_col.squeeze(), x[:, 2])
        
        # Test first_two_rows_three_cols
        assert first_two_rows_three_cols.shape == (2, 3)
        assert torch.allclose(first_two_rows_three_cols, x[:2, :3])
        
        # Test even_rows_odd_cols (even rows: 0, 2; odd cols: 1, 3)
        assert even_rows_odd_cols.shape == (2, 2)
        expected = torch.tensor([[x[0, 1], x[0, 3]], [x[2, 1], x[2, 3]]])
        assert torch.allclose(even_rows_odd_cols, expected)
    
    def test_slice_assignment_practice(self):
        """Test slice_assignment_practice function"""
        # Test with minimum size
        x = torch.zeros(4, 6)
        result = slice_assignment_practice(x)
        
        expected = torch.tensor([
            [0, 1, 2, 2, 2, 2],
            [0, 1, 2, 2, 2, 2],
            [3, 4, 3, 4, 5, 5],
            [3, 4, 3, 4, 5, 5]
        ], dtype=torch.float32)
        
        assert torch.allclose(result[:4, :6], expected)
        
        # Test with larger tensor
        x = torch.ones(6, 8)
        result = slice_assignment_practice(x)
        
        # Check that only first 4x6 is modified
        assert torch.allclose(result[:4, :6], expected)
        # Check that other elements remain unchanged (were 1.0)
        assert torch.all(result[4:, :] == 1.0)
        assert torch.all(result[:, 6:] == 1.0)
    
    def test_shuffle_cols(self):
        """Test shuffle_cols function"""
        x = torch.arange(12).reshape(3, 4)  # 3x4 tensor
        
        y = shuffle_cols(x)
        
        assert y.shape == (3, 4)
        # First two columns should be copies of first column
        assert torch.allclose(y[:, 0], x[:, 0])
        assert torch.allclose(y[:, 1], x[:, 0])
        # Third column should be same as third column of x
        assert torch.allclose(y[:, 2], x[:, 2])
        # Fourth column should be same as second column of x
        assert torch.allclose(y[:, 3], x[:, 1])
    
    def test_reverse_rows(self):
        """Test reverse_rows function"""
        x = torch.arange(12).reshape(3, 4)
        
        y = reverse_rows(x)
        
        assert y.shape == x.shape
        # Check rows are reversed
        assert torch.allclose(y[0], x[-1])
        assert torch.allclose(y[1], x[-2])
        assert torch.allclose(y[2], x[0])
    
    def test_take_one_elem_per_col(self):
        """Test take_one_elem_per_col function"""
        x = torch.arange(20).reshape(5, 4)  # 5x4 tensor
        
        y = take_one_elem_per_col(x)
        
        assert y.shape == (3,)
        # Second element of first column
        assert y[0] == x[1, 0]
        # First element of second column
        assert y[1] == x[0, 1]
        # Fourth element of third column
        assert y[2] == x[3, 2]
    
    def test_make_one_hot(self):
        """Test make_one_hot function"""
        # Test basic case
        x = [0, 1, 2, 0]
        y = make_one_hot(x)
        
        assert y.shape == (4, 3)  # N=4, C=1+max(x)=3
        assert y.dtype == torch.float32
        
        # Check one-hot encoding
        expected = torch.tensor([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0]
        ])
        assert torch.allclose(y, expected)
        
        # Test with non-consecutive values
        x = [2, 5, 1]
        y = make_one_hot(x)
        assert y.shape == (3, 6)  # N=3, C=1+max(x)=6
    
    def test_sum_positive_entries(self):
        """Test sum_positive_entries function"""
        x = torch.tensor([[-1, 2, 0], [0, 5, -3], [8, -9, 0]], dtype=torch.int64)
        result = sum_positive_entries(x)
        assert result == 15  # 2 + 5 + 8
        
        # Test with all negative
        x = torch.tensor([-1, -2, -3], dtype=torch.int64)
        assert sum_positive_entries(x) == 0
        
        # Test with all positive
        x = torch.tensor([1, 2, 3], dtype=torch.int64)
        assert sum_positive_entries(x) == 6
    
    def test_reshape_practice(self):
        """Test reshape_practice function"""
        x = torch.arange(24, dtype=torch.float32)
        y = reshape_practice(x)
        
        assert y.shape == (3, 8)
        
        # Check specific pattern
        expected = torch.tensor([
            [0, 1, 2, 3, 12, 13, 14, 15],
            [4, 5, 6, 7, 16, 17, 18, 19],
            [8, 9, 10, 11, 20, 21, 22, 23]
        ], dtype=torch.float32)
        
        assert torch.allclose(y, expected)
    
    def test_zero_row_min(self):
        """Test zero_row_min function"""
        x = torch.tensor([[10, 20, 30], [2, 5, 1]], dtype=torch.float32)
        y = zero_row_min(x)
        
        expected = torch.tensor([[0, 20, 30], [2, 5, 0]], dtype=torch.float32)
        assert torch.allclose(y, expected)
        
        # Test with negative values
        x = torch.tensor([[-1, -5, 3], [0, 2, 1]], dtype=torch.float32)
        y = zero_row_min(x)
        expected = torch.tensor([[-1, 0, 3], [0, 2, 1]], dtype=torch.float32)
        assert torch.allclose(y, expected)
    
    def test_batched_matrix_multiply_loop(self):
        """Test batched_matrix_multiply_loop function"""
        # Test with batch size 2
        x = torch.randn(2, 3, 4)
        y = torch.randn(2, 4, 5)
        result = batched_matrix_multiply_loop(x, y)
        
        assert result.shape == (2, 3, 5)
        
        # Check first batch manually
        expected_0 = torch.mm(x[0], y[0])
        assert torch.allclose(result[0], expected_0)
        
        # Check second batch manually
        expected_1 = torch.mm(x[1], y[1])
        assert torch.allclose(result[1], expected_1)
    
    def test_batched_matrix_multiply_noloop(self):
        """Test batched_matrix_multiply_noloop function"""
        # Test with batch size 3
        x = torch.randn(3, 2, 4)
        y = torch.randn(3, 4, 3)
        result = batched_matrix_multiply_noloop(x, y)
        
        assert result.shape == (3, 2, 3)
        
        # Compare with loop version
        expected = batched_matrix_multiply_loop(x, y)
        assert torch.allclose(result, expected)
    
    def test_normalize_columns(self):
        """Test normalize_columns function"""
        x = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]], dtype=torch.float32)
        y = normalize_columns(x)
        
        assert y.shape == x.shape
        
        # Check that each column has mean 0 and std 1
        for j in range(y.shape[1]):
            col = y[:, j]
            mean = col.mean()
            std = col.std()
            
            # Allow for small numerical errors
            assert abs(mean) < 1e-6
            assert abs(std - 1.0) < 1e-6
    
    def test_mm_on_gpu(self):
        """Test mm_on_gpu function"""
        # Create test tensors
        x = torch.randn(3, 4)
        w = torch.randn(4, 5)
        
        # Compute on CPU
        expected = torch.mm(x, w)
        
        # Compute using GPU function
        result = mm_on_gpu(x, w)
        
        # Check result is on CPU and correct
        assert result.device.type == 'cpu'
        assert torch.allclose(result, expected)
    
    def test_challenge_mean_tensors(self):
        """Test challenge_mean_tensors function"""
        # Create test tensors of different lengths
        xs = [
            torch.tensor([1.0, 2.0, 3.0]),
            torch.tensor([4.0, 5.0]),
            torch.tensor([6.0, 7.0, 8.0, 9.0])
        ]
        ls = torch.tensor([3, 2, 4])
        
        result = challenge_mean_tensors(xs, ls)
        
        assert result.shape == (3,)
        assert abs(result[0].item() - 2.0) < 1e-6  # (1+2+3)/3 = 2
        assert abs(result[1].item() - 4.5) < 1e-6  # (4+5)/2 = 4.5
        assert abs(result[2].item() - 7.5) < 1e-6  # (6+7+8+9)/4 = 7.5
    
    def test_challenge_get_uniques(self):
        """Test challenge_get_uniques function"""
        # Test with duplicates
        x = torch.tensor([3, 1, 4, 1, 5, 9, 2, 6, 5, 3])
        uniques, indices = challenge_get_uniques(x)
        
        # Check that we get the right unique values
        expected_uniques = torch.tensor([1, 2, 3, 4, 5, 6, 9])
        assert uniques.shape[0] == 7
        for val in expected_uniques:
            assert val in uniques
        
        # Check that indices point to first occurrences
        for i, val in enumerate(uniques):
            assert x[indices[i]] == val
        
        # Check that indices are in increasing order (first occurrences)
        assert torch.all(indices[:-1] < indices[1:])
        
        # Test with no duplicates
        x = torch.tensor([1, 2, 3, 4, 5])
        uniques, indices = challenge_get_uniques(x)
        assert torch.allclose(uniques, x)
        assert torch.allclose(indices, torch.arange(5))

if __name__ == "__main__":
    pytest.main([__file__])