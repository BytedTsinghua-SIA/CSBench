"""
Unit tests for PeakProblem class and peak-finding utilities.

Tests cover basic functionality of the PeakProblem class including
matrix creation, peak detection, and neighbor operations.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import peak


class TestPeakProblemCreation:
    """Test PeakProblem creation and initialization."""
    
    def test_create_single_element_matrix(self):
        """Test creating a problem from a 1x1 matrix."""
        matrix = [[5]]
        problem = peak.createProblem(matrix)
        assert problem.numRow == 1
        assert problem.numCol == 1
        assert problem.get((0, 0)) == 5
    
    def test_create_small_matrix(self):
        """Test creating a problem from a small matrix."""
        matrix = [[1, 2], [3, 4]]
        problem = peak.createProblem(matrix)
        assert problem.numRow == 2
        assert problem.numCol == 2
        assert problem.get((0, 0)) == 1
        assert problem.get((1, 1)) == 4
    
    def test_create_large_matrix(self):
        """Test creating a problem from a larger matrix."""
        matrix = [[i * 10 + j for j in range(5)] for i in range(5)]
        problem = peak.createProblem(matrix)
        assert problem.numRow == 5
        assert problem.numCol == 5
        assert problem.get((2, 3)) == 23
    
    def test_create_rectangular_matrix(self):
        """Test creating a problem from a rectangular matrix."""
        matrix = [[1, 2, 3], [4, 5, 6]]
        problem = peak.createProblem(matrix)
        assert problem.numRow == 2
        assert problem.numCol == 3
    
    def test_create_empty_matrix(self):
        """Test creating a problem from an empty matrix."""
        matrix = []
        problem = peak.createProblem(matrix)
        assert problem.numRow == 0
        assert problem.numCol == 0


class TestPeakProblemGet:
    """Test PeakProblem get method."""
    
    def test_get_valid_location(self):
        """Test getting value from valid location."""
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        problem = peak.createProblem(matrix)
        assert problem.get((1, 1)) == 5
        assert problem.get((0, 2)) == 3
        assert problem.get((2, 0)) == 7
    
    def test_get_invalid_row(self):
        """Test getting value from invalid row returns 0."""
        matrix = [[1, 2], [3, 4]]
        problem = peak.createProblem(matrix)
        assert problem.get((-1, 0)) == 0
        assert problem.get((2, 0)) == 0
    
    def test_get_invalid_column(self):
        """Test getting value from invalid column returns 0."""
        matrix = [[1, 2], [3, 4]]
        problem = peak.createProblem(matrix)
        assert problem.get((0, -1)) == 0
        assert problem.get((0, 2)) == 0


class TestPeakProblemIsPeak:
    """Test peak detection functionality."""
    
    def test_single_element_is_peak(self):
        """Test that single element matrix has a peak."""
        matrix = [[5]]
        problem = peak.createProblem(matrix)
        assert problem.isPeak((0, 0)) is True
    
    def test_center_peak_in_small_matrix(self):
        """Test detecting peak in center of small matrix."""
        matrix = [[1, 2, 1], [2, 5, 2], [1, 2, 1]]
        problem = peak.createProblem(matrix)
        assert problem.isPeak((1, 1)) is True
    
    def test_corner_peak(self):
        """Test detecting peak at corner."""
        matrix = [[10, 5], [5, 3]]
        problem = peak.createProblem(matrix)
        assert problem.isPeak((0, 0)) is True
    
    def test_edge_peak(self):
        """Test detecting peak at edge."""
        matrix = [[5, 10, 5], [3, 4, 3]]
        problem = peak.createProblem(matrix)
        assert problem.isPeak((0, 1)) is True
    
    def test_non_peak_location(self):
        """Test that non-peak location returns False."""
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        problem = peak.createProblem(matrix)
        assert problem.isPeak((0, 0)) is False
        assert problem.isPeak((1, 1)) is False


class TestPeakProblemGetBetterNeighbor:
    """Test getBetterNeighbor functionality."""
    
    def test_get_better_neighbor(self):
        """Test getBetterNeighbor on various scenarios."""
        test_cases = [
            ([[1, 2, 1], [2, 5, 2], [1, 2, 1]], (1, 1), (1, 1)),  # Peak returns self
            ([[10, 5], [5, 3]], (1, 0), (0, 0)),  # North neighbor
            ([[5, 10], [3, 5]], (0, 0), (0, 1))  # East neighbor
        ]
        for matrix, location, expected in test_cases:
            problem = peak.createProblem(matrix)
            result = problem.getBetterNeighbor(location)
            assert result == expected


class TestPeakProblemGetMaximum:
    """Test getMaximum functionality."""
    
    def test_get_maximum(self):
        """Test getMaximum on various location sets."""
        test_cases = [
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [(1, 1)], (1, 1)),
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [(0, 0), (1, 1), (2, 2)], (2, 2)),
            ([[1, 5, 3], [4, 2, 6], [7, 8, 9]], [(0, 0), (0, 1), (0, 2)], (0, 1))
        ]
        for matrix, locations, expected in test_cases:
            problem = peak.createProblem(matrix)
            result = problem.getMaximum(locations)
            assert result == expected


class TestPeakProblemSubproblem:
    """Test subproblem creation and operations."""
    
    def test_get_subproblem(self):
        """Test creating a subproblem."""
        matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        problem = peak.createProblem(matrix)
        subproblem = problem.getSubproblem((1, 1, 2, 2))
        assert subproblem.numRow == 2
        assert subproblem.numCol == 2
        assert subproblem.get((0, 0)) == 6
    
    def test_get_location_in_self(self):
        """Test remapping location from subproblem to original."""
        matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        problem = peak.createProblem(matrix)
        subproblem = problem.getSubproblem((1, 1, 2, 2))
        location_in_sub = (0, 0)
        location_in_original = problem.getLocationInSelf(subproblem, location_in_sub)
        assert location_in_original == (1, 1)
    
    def test_get_subproblem_containing(self):
        """Test finding subproblem containing a location."""
        matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        problem = peak.createProblem(matrix)
        boundList = [(0, 0, 2, 2), (0, 2, 2, 2), (2, 0, 1, 4)]
        location = (1, 3)
        subproblem = problem.getSubproblemContaining(boundList, location)
        assert subproblem.startRow == 0
        assert subproblem.startCol == 2

