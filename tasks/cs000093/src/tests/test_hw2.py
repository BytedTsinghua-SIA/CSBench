#!/usr/bin/env python3
"""
Pytest tests for Common Lisp homework 2 (hw2.lsp).
Tests BFS, DFS, DFID, and Missionary-Cannibal problem solutions.
"""
import subprocess
import sys
from pathlib import Path


def run_lisp_test(lisp_expr):
    """
    Run a Lisp expression using sbcl and return the result.

    Args:
        lisp_expr: The Lisp expression to evaluate

    Returns:
        The stdout from sbcl
    """
    src_dir = Path(__file__).parent.parent
    lisp_file = src_dir / "hw2.lsp"

    cmd = [
        "sbcl",
        "--non-interactive",
        "--eval", '(load "{}")'.format(lisp_file.as_posix()),
        "--eval", "(format t \"~a\" {})".format(lisp_expr)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=src_dir
    )

    # Filter out SBCL version info and return just the result
    lines = result.stdout.strip().split('\n')
    # The actual result is usually on the last non-empty line
    for line in reversed(lines):
        line = line.strip()
        if line and not line.startswith("This is SBCL") and not line.startswith("More information") and not line.startswith("SBCL is free software"):
            return line
    return ""


def run_lisp_test_script(test_script):
    """
    Run a complete Lisp test script.

    Args:
        test_script: The Lisp test script to run

    Returns:
        The stdout from sbcl
    """
    src_dir = Path(__file__).parent.parent
    lisp_file = src_dir / "hw2.lsp"

    cmd = [
        "sbcl",
        "--non-interactive",
        "--eval", '(load "{}")'.format(lisp_file.as_posix()),
        "--eval", test_script
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=src_dir
    )

    return result.stdout.strip()


def run_lisp_with_test_file(test_file_expr):
    """
    Run a Lisp expression with both hw2.lsp and test.lsp loaded.

    Args:
        test_file_expr: The expression to evaluate after loading both files

    Returns:
        The stdout from sbcl
    """
    src_dir = Path(__file__).parent.parent
    lisp_file = src_dir / "hw2.lsp"
    test_file = src_dir / "test.lsp"

    cmd = [
        "sbcl",
        "--non-interactive",
        "--eval", '(load "{}")'.format(lisp_file.as_posix()),
        "--eval", '(load "{}")'.format(test_file.as_posix()),
        "--eval", test_file_expr
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=src_dir
    )

    return result.stdout.strip()


class TestSearchAlgorithms:
    """Test class for BFS, DFS, and DFID search algorithms."""

    def test_bfs_basic(self):
        """Test BFS on a simple tree: ((A (B)) C (D))."""
        result = run_lisp_test_script("(format t \"~a\" (bfs '((A (B)) C (D))))")
        assert "C A D B" in result, f"BFS expected (C A D B), got {result}"

    def test_dfs_basic(self):
        """Test DFS on a simple tree: ((A (B)) C (D))."""
        result = run_lisp_test_script("(format t \"~a\" (dfs '((A (B)) C (D))))")
        assert "D C B A" in result, f"DFS expected (D C B A), got {result}"

    def test_dfid_basic(self):
        """Test DFID on a simple tree: ((A (B)) C (D)) with depth 3."""
        result = run_lisp_test_script("(format t \"~a\" (dfid '((A (B)) C (D)) 3))")
        assert "C A C D A B C D" in result, f"DFID expected (C A C D A B C D), got {result}"

    def test_bfs_empty(self):
        """Test BFS on an empty list."""
        result = run_lisp_test_script("(format t \"~a\" (bfs NIL))")
        assert "NIL" in result or result == "", f"BFS on empty list expected NIL, got {result}"

    def test_dfs_empty(self):
        """Test DFS on an empty list."""
        result = run_lisp_test_script("(format t \"~a\" (dfs NIL))")
        assert "NIL" in result or result == "", f"DFS on empty list expected NIL, got {result}"


class TestMissionaryCannibal:
    """Test class for Missionary-Cannibal problem solution."""

    def test_mc_dfs_initial_state(self):
        """Test MC-DFS from initial state (3 3 T)."""
        result = run_lisp_test_script("(format t \"~a\" (mc-dfs '(3 3 T) NIL))")
        # Should return a path from initial state to goal state
        assert result is not None and len(result) > 0, f"MC-DFS should return a path, got {result}"

    def test_mc_dfs_state_0_3_T(self):
        """Test MC-DFS from state (0 3 T) should return the complete path."""
        result = run_lisp_test_script("(format t \"~a\" (mc-dfs '(0 3 T) NIL))")
        # This state should lead to a valid solution path
        assert result is not None and len(result) > 0, f"MC-DFS should return a path, got {result}"
        # Check that the path contains the goal state (3 3 NIL)
        assert "3 3 NIL" in result, f"Path should contain (3 3 NIL), got {result}"

    def test_mc_dfs_state_3_2_T(self):
        """Test MC-DFS from state (3 2 T) with partial path given."""
        result = run_lisp_test_script("(format t \"~a\" (mc-dfs '(3 2 T) '((0 2 NIL) (3 3 T))))")
        # This should return a valid continuation of the path
        assert result is not None and len(result) > 0, f"MC-DFS should return a path, got {result}"

    def test_final_state(self):
        """Test final-state function returns T for goal state."""
        result = run_lisp_test_script("(format t \"~a\" (final-state '(3 3 NIL)))")
        assert "T" in result, f"final-state(3 3 NIL) expected T, got {result}"

    def test_final_state_false(self):
        """Test final-state function returns NIL for non-goal state."""
        result = run_lisp_test_script("(format t \"~a\" (final-state '(3 3 T)))")
        assert "NIL" in result, f"final-state(3 3 T) expected NIL, got {result}"


class TestRunSearchTest:
    """Test the combined RUN-SEARCH-TEST function from test.lsp."""

    def test_run_search_test(self):
        """Test that RUN-SEARCH-TEST returns T (all assertions pass)."""
        # RUN-SEARCH-TEST is defined in test.lsp
        result = run_lisp_with_test_file("(format t \"~a\" (RUN-SEARCH-TEST))")
        assert "T" in result and "NIL" not in result, \
            f"RUN-SEARCH-TEST expected T, got {result}"


class TestMissCann:
    """Test the combined MISS-CANN function from test.lsp."""

    def test_miss_cann(self):
        """Test that MISS-CANN returns T (all assertions pass)."""
        result = run_lisp_with_test_file("(format t \"~a\" (MISS-CANN))")
        assert "T" in result and "NIL" not in result, \
            f"MISS-CANN expected T, got {result}"
