"""
Pytest unit tests for Reassembler functionality.

These tests correspond to the Reassembler component from Lab Checkpoint 1,
which stitches received substrings into a contiguous byte stream.

Functionality tested (per task.md):
- Receive substrings (segments) of a byte stream, potentially out of order, duplicated, or overlapping
- Reassemble them into a contiguous stream of bytes
- Write available bytes to the ByteStream as soon as they are known
- Store "unassembled" bytes that fit within the capacity but cannot be written yet
- Discard bytes that lie beyond the stream's available capacity
- Interface: insert(), count_bytes_pending(), reader()

Note: Tests can only PASS or FAIL, never ERROR.
"""

import pytest


class TestReassemblerBasic:
    """Test basic Reassembler operations."""
    
    def test_reassembler_single(self, cpp_test_runner):
        """
        Test Reassembler with single substring insertions.
        
        Verifies:
        - Reassembler can be constructed properly
        - Single substring insertion at index 0 works
        - Empty string handling (including "is_last" flag)
        - Proper closing of stream with is_last_substring flag
        """
        passed, message = cpp_test_runner("reassembler_single")
        assert passed, message


class TestReassemblerCapacity:
    """Test Reassembler capacity management."""
    
    def test_reassembler_capacity(self, cpp_test_runner):
        """
        Test Reassembler capacity constraints.
        
        Verifies:
        - Bytes beyond stream's available capacity are discarded
        - Internal storage respects capacity limit for both buffered bytes 
          in ByteStream and unassembled substrings
        - count_bytes_pending() returns correct values
        """
        passed, message = cpp_test_runner("reassembler_cap")
        assert passed, message


class TestReassemblerSequence:
    """Test Reassembler sequential operations."""
    
    def test_reassembler_sequential(self, cpp_test_runner):
        """
        Test Reassembler with sequential (in-order) substring insertion.
        
        Verifies:
        - Contiguous substrings are written to ByteStream immediately
        - bytes_pushed tracking is correct
        - Stream completion with is_last_substring
        """
        passed, message = cpp_test_runner("reassembler_seq")
        assert passed, message


class TestReassemblerOutOfOrder:
    """Test Reassembler with out-of-order data."""
    
    def test_reassembler_holes(self, cpp_test_runner):
        """
        Test Reassembler with gaps (holes) in the byte stream.
        
        Verifies:
        - Out-of-order segments are stored correctly
        - Segments are only written to ByteStream when contiguous
        - count_bytes_pending() correctly tracks unassembled bytes
        """
        passed, message = cpp_test_runner("reassembler_holes")
        assert passed, message


class TestReassemblerDuplicates:
    """Test Reassembler with duplicate data."""
    
    def test_reassembler_duplicates(self, cpp_test_runner):
        """
        Test Reassembler handling of duplicate substrings.
        
        Verifies:
        - Duplicate data is correctly deduplicated
        - Internal storage only keeps one copy of data
        - No double-counting of bytes
        """
        passed, message = cpp_test_runner("reassembler_dup")
        assert passed, message


class TestReassemblerOverlapping:
    """Test Reassembler with overlapping data."""
    
    def test_reassembler_overlapping(self, cpp_test_runner):
        """
        Test Reassembler handling of overlapping substrings.
        
        Verifies:
        - Overlapping segments are handled efficiently
        - Only one copy of overlapping data is stored
        - Correct bytes are written to ByteStream
        """
        passed, message = cpp_test_runner("reassembler_overlapping")
        assert passed, message


class TestReassemblerWindow:
    """Test Reassembler sliding window behavior."""
    
    def test_reassembler_window(self, cpp_test_runner):
        """
        Test Reassembler sliding window management.
        
        Verifies:
        - Window advances as data is consumed from ByteStream
        - Data outside the window is correctly handled
        - Capacity constraints are respected dynamically
        """
        passed, message = cpp_test_runner("reassembler_win", timeout=60)
        assert passed, message
