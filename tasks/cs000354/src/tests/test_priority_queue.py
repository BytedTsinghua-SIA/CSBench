"""
Unit tests for PriorityQueue class.

Tests cover basic operations, edge cases, and heap property maintenance.
"""
import sys
import os

# Add parent directory to path to import circuit module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'circuit'))

from circuit import PriorityQueue


class TestPriorityQueueBasic:
    """Test basic PriorityQueue operations."""
    
    def test_empty_queue_length(self):
        """Test that empty queue has length 0."""
        queue = PriorityQueue()
        assert len(queue) == 0
    
    def test_empty_queue_min(self):
        """Test that min() returns None for empty queue."""
        queue = PriorityQueue()
        assert queue.min() is None
    
    def test_empty_queue_pop(self):
        """Test that pop() returns None for empty queue."""
        queue = PriorityQueue()
        assert queue.pop() is None
    
    def test_single_element_append(self):
        """Test appending a single element."""
        queue = PriorityQueue()
        queue.append(5)
        assert len(queue) == 1
    
    def test_single_element_min(self):
        """Test min() with single element."""
        queue = PriorityQueue()
        queue.append(5)
        assert queue.min() == 5
    
    def test_single_element_pop(self):
        """Test pop() with single element."""
        queue = PriorityQueue()
        queue.append(5)
        result = queue.pop()
        assert result == 5
        assert len(queue) == 0
    
    def test_multiple_elements_ordered(self):
        """Test that elements are popped in correct order."""
        queue = PriorityQueue()
        values = [3, 1, 4, 1, 5, 9, 2, 6]
        for val in values:
            queue.append(val)
        
        expected = sorted(values)
        for exp in expected:
            assert queue.pop() == exp
        assert len(queue) == 0
    
    def test_duplicate_values(self):
        """Test handling of duplicate values."""
        queue = PriorityQueue()
        queue.append(5)
        queue.append(3)
        queue.append(5)
        queue.append(3)
        
        assert queue.pop() == 3
        assert queue.pop() == 3
        assert queue.pop() == 5
        assert queue.pop() == 5
        assert len(queue) == 0
    
    def test_large_sequence(self):
        """Test with larger sequence of elements."""
        queue = PriorityQueue()
        values = list(range(100, 0, -1))
        for val in values:
            queue.append(val)
        
        for i in range(1, 101):
            assert queue.pop() == i
        assert len(queue) == 0


class TestPriorityQueueEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_negative_values(self):
        """Test with negative values."""
        queue = PriorityQueue()
        queue.append(-5)
        queue.append(0)
        queue.append(-10)
        queue.append(5)
        
        assert queue.pop() == -10
        assert queue.pop() == -5
        assert queue.pop() == 0
        assert queue.pop() == 5
    
    def test_zero_value(self):
        """Test with zero value."""
        queue = PriorityQueue()
        queue.append(0)
        assert queue.min() == 0
        assert queue.pop() == 0
    
    def test_very_large_values(self):
        """Test with very large values."""
        queue = PriorityQueue()
        large_val = 10**10
        queue.append(large_val)
        queue.append(large_val - 1)
        queue.append(large_val + 1)
        
        assert queue.pop() == large_val - 1
        assert queue.pop() == large_val
        assert queue.pop() == large_val + 1
    
    def test_append_none_raises_error(self):
        """Test that appending None raises ValueError."""
        queue = PriorityQueue()
        try:
            queue.append(None)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    
    def test_interleaved_operations(self):
        """Test interleaved append and pop operations."""
        queue = PriorityQueue()
        queue.append(5)
        queue.append(2)
        assert queue.pop() == 2
        queue.append(8)
        queue.append(1)
        assert queue.pop() == 1
        assert queue.pop() == 5
        assert queue.pop() == 8


class TestPriorityQueueHeapProperty:
    """Test that PriorityQueue maintains heap property."""
    
    def test_heap_property_after_append(self):
        """Test that heap property is maintained after append."""
        queue = PriorityQueue()
        values = [10, 5, 15, 3, 7, 12, 20]
        for val in values:
            queue.append(val)
            # After each append, min should be the smallest so far
            assert queue.min() == min(values[:len(queue)])
    
    def test_heap_property_after_pop(self):
        """Test that heap property is maintained after pop."""
        queue = PriorityQueue()
        values = [10, 5, 15, 3, 7, 12, 20]
        for val in values:
            queue.append(val)
        
        sorted_vals = sorted(values)
        for i, expected in enumerate(sorted_vals):
            assert queue.pop() == expected
            if len(queue) > 0:
                # Remaining minimum should be next in sorted order
                assert queue.min() == sorted_vals[i + 1]
    
    def test_reverse_order_insertion(self):
        """Test insertion in reverse order."""
        queue = PriorityQueue()
        for i in range(10, 0, -1):
            queue.append(i)
        
        for i in range(1, 11):
            assert queue.pop() == i
    
    def test_sorted_order_insertion(self):
        """Test insertion in sorted order."""
        queue = PriorityQueue()
        for i in range(1, 11):
            queue.append(i)
        
        for i in range(1, 11):
            assert queue.pop() == i


class TestPriorityQueueWithComparableObjects:
    """Test PriorityQueue with comparable objects like Transition."""
    
    def test_with_simple_comparable(self):
        """Test with simple comparable objects."""
        class ComparableItem:
            def __init__(self, value):
                self.value = value
            def __lt__(self, other):
                return self.value < other.value
            def __le__(self, other):
                return self.value <= other.value
            def __gt__(self, other):
                return self.value > other.value
            def __ge__(self, other):
                return self.value >= other.value
        
        queue = PriorityQueue()
        items = [ComparableItem(5), ComparableItem(2), ComparableItem(8)]
        for item in items:
            queue.append(item)
        
        assert queue.pop().value == 2
        assert queue.pop().value == 5
        assert queue.pop().value == 8
    
    def test_with_time_based_comparison(self):
        """Test with time-based comparison similar to Transition."""
        class TimeItem:
            def __init__(self, time, obj_id):
                self.time = time
                self.obj_id = obj_id
            def __lt__(self, other):
                return (self.time < other.time or
                       (self.time == other.time and self.obj_id < other.obj_id))
            def __le__(self, other):
                return (self.time < other.time or
                       (self.time == other.time and self.obj_id <= other.obj_id))
            def __gt__(self, other):
                return (self.time > other.time or
                       (self.time == other.time and self.obj_id > other.obj_id))
            def __ge__(self, other):
                return (self.time > other.time or
                       (self.time == other.time and self.obj_id >= other.obj_id))
        
        queue = PriorityQueue()
        items = [
            TimeItem(10, 2),
            TimeItem(5, 1),
            TimeItem(10, 0),
            TimeItem(3, 0)
        ]
        for item in items:
            queue.append(item)
        
        # Should pop in order: (3,0), (5,1), (10,0), (10,2)
        result1 = queue.pop()
        assert result1.time == 3 and result1.obj_id == 0
        result2 = queue.pop()
        assert result2.time == 5 and result2.obj_id == 1
        result3 = queue.pop()
        assert result3.time == 10 and result3.obj_id == 0
        result4 = queue.pop()
        assert result4.time == 10 and result4.obj_id == 2
    
    def test_heapify_down_with_only_left_child(self):
        """Test heapify_down when node has only left child."""
        queue = PriorityQueue()
        # Create a scenario where root has only left child
        # Insert elements to create specific heap structure
        queue.append(10)
        queue.append(5)
        queue.append(15)
        queue.append(3)
        queue.append(7)
        # Now pop to trigger heapify_down with only left child scenario
        assert queue.pop() == 3
        assert queue.pop() == 5
        assert queue.pop() == 7
        assert queue.pop() == 10
        assert queue.pop() == 15
    
    def test_heapify_down_with_leaf_node(self):
        """Test heapify_down when node is a leaf (no children)."""
        queue = PriorityQueue()
        queue.append(1)
        queue.append(2)
        # After popping 1, 2 becomes root and is a leaf
        assert queue.pop() == 1
        assert queue.pop() == 2
        # Queue is now empty, next pop should return None
        assert queue.pop() is None
    
    def test_sequential_operations_maintain_heap(self):
        """Test that sequential append and pop operations maintain heap property."""
        queue = PriorityQueue()
        # Add elements
        for val in [5, 2, 8, 1, 9, 3]:
            queue.append(val)
        
        # Pop some elements
        assert queue.pop() == 1
        assert queue.pop() == 2
        
        # Add more elements
        queue.append(4)
        queue.append(0)
        
        # Verify heap property is maintained
        assert queue.min() == 0
        assert queue.pop() == 0
        assert queue.pop() == 3
        assert queue.pop() == 4
        assert queue.pop() == 5
        assert queue.pop() == 8
        assert queue.pop() == 9

