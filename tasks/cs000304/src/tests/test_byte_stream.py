"""
Pytest unit tests for ByteStream functionality.

These tests correspond to the ByteStream component from Lab Checkpoint 0/1,
which implements an in-memory reliable byte stream with Writer and Reader interfaces.

Functionality tested:
- Writer interface: push(), close(), is_closed(), available_capacity(), bytes_pushed()
- Reader interface: peek(), pop(), is_finished(), bytes_buffered(), bytes_popped()
- Capacity management and flow control

Note: Tests can only PASS or FAIL, never ERROR.
"""

import pytest


class TestByteStreamBasics:
    """Test basic ByteStream operations."""
    
    def test_byte_stream_basics(self, cpp_test_runner):
        """
        Test basic ByteStream construction and simple operations.
        
        Verifies:
        - ByteStream can be constructed with a capacity
        - Basic push/peek/pop operations work correctly
        - Stream state tracking (is_closed, is_finished)
        """
        passed, message = cpp_test_runner("byte_stream_basics")
        assert passed, message
    
    def test_byte_stream_capacity(self, cpp_test_runner):
        """
        Test ByteStream capacity management.
        
        Verifies:
        - available_capacity() returns correct values
        - Push operations respect capacity limits
        - Capacity is freed after pop operations
        """
        passed, message = cpp_test_runner("byte_stream_capacity")
        assert passed, message


class TestByteStreamWrite:
    """Test ByteStream write operations."""
    
    def test_byte_stream_one_write(self, cpp_test_runner):
        """
        Test ByteStream with a single write operation.
        
        Verifies:
        - Single push operation correctly stores data
        - bytes_pushed() returns correct count
        - Data can be read back correctly
        """
        passed, message = cpp_test_runner("byte_stream_one_write")
        assert passed, message
    
    def test_byte_stream_two_writes(self, cpp_test_runner):
        """
        Test ByteStream with two consecutive write operations.
        
        Verifies:
        - Multiple push operations work correctly
        - Data is concatenated in order
        - Cumulative bytes_pushed() is correct
        """
        passed, message = cpp_test_runner("byte_stream_two_writes")
        assert passed, message
    
    def test_byte_stream_many_writes(self, cpp_test_runner):
        """
        Test ByteStream with many write operations.
        
        Verifies:
        - Stream handles multiple sequential writes
        - Data integrity is maintained across many operations
        - Memory management works correctly
        """
        passed, message = cpp_test_runner("byte_stream_many_writes")
        assert passed, message


class TestByteStreamStress:
    """Stress tests for ByteStream."""
    
    def test_byte_stream_stress_test(self, cpp_test_runner):
        """
        Stress test ByteStream with intensive operations.
        
        Verifies:
        - Stream remains stable under heavy load
        - No memory leaks or corruption
        - All state tracking remains accurate
        """
        passed, message = cpp_test_runner("byte_stream_stress_test", timeout=60)
        assert passed, message


class TestByteStreamConstraints:
    """Test ByteStream implementation constraints."""
    
    def test_no_skip_implementation(self, cpp_test_runner):
        """
        Verify implementation does not skip any required functionality.
        
        This test ensures all required methods are properly implemented
        and not just returning placeholder values.
        """
        passed, message = cpp_test_runner("no_skip")
        assert passed, message
