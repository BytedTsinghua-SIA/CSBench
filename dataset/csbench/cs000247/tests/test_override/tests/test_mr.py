"""
Pytest tests for MapReduce implementation.
These tests wrap the Go test script (test-mr.sh).
The test script is run once and results are cached for all assertions.
"""
import os
import subprocess
import sys
import pytest


# Cached storage for test results
_test_output = None
_test_result = None


def run_go_test_once(script_name="test-mr.sh"):
    """
    Run the Go test script once and cache the result.
    Subsequent calls return the cached result.
    """
    global _test_output, _test_result

    if _test_output is not None:
        return _test_result

    script_dir = os.path.join(os.path.dirname(__file__), "..", "src", "main")
    script_path = os.path.join(script_dir, script_name)

    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Test script not found: {script_path}")

    result = subprocess.run(
        ["bash", script_path],
        cwd=script_dir,
        capture_output=True,
        text=True,
        timeout=600
    )

    _test_output = result.stdout + result.stderr
    _test_result = result

    return result


def get_test_output():
    """Get the cached test output."""
    global _test_output
    if _test_output is None:
        run_go_test_once()
    return _test_output


def test_mapreduce_word_count():
    """
    Test word count using MapReduce.
    Verifies that the wc test passes.
    """
    output = get_test_output()

    # Check for wc test pass
    assert "wc test: PASS" in output, f"Word count test failed:\n{output}"


def test_mapreduce_indexer():
    """
    Test indexer using MapReduce.
    Verifies that the indexer test passes.
    """
    output = get_test_output()

    # Check for indexer test pass
    assert "indexer test: PASS" in output, f"Indexer test failed:\n{output}"


def test_map_parallelism():
    """
    Test map parallelism.
    Verifies that map tasks run in parallel.
    """
    output = get_test_output()

    # Check for map parallelism test pass
    assert "map parallelism test: PASS" in output, f"Map parallelism test failed:\n{output}"


def test_reduce_parallelism():
    """
    Test reduce parallelism.
    Verifies that reduce tasks run in parallel.
    """
    output = get_test_output()

    # Check for reduce parallelism test pass
    assert "reduce parallelism test: PASS" in output, f"Reduce parallelism test failed:\n{output}"


def test_job_count():
    """
    Test job count.
    Verifies that map jobs run correct number of times.
    """
    output = get_test_output()

    # Check for job count test pass
    assert "job count test: PASS" in output, f"Job count test failed:\n{output}"


def test_early_exit():
    """
    Test early exit behavior.
    Verifies that no worker or coordinator exits before task completion.
    """
    output = get_test_output()

    # Check for early exit test pass
    assert "early exit test: PASS" in output, f"Early exit test failed:\n{output}"


def test_crash_recovery():
    """
    Test crash recovery.
    Verifies that workers can crash and the job still completes.
    """
    output = get_test_output()

    # Check for crash test pass
    assert "crash test: PASS" in output, f"Crash recovery test failed:\n{output}"


def test_all_tests_passed():
    """
    Test that all MapReduce tests pass.
    This is a comprehensive test that runs all test cases.
    """
    result = run_go_test_once()
    output = get_test_output()

    # Check for all tests pass message
    assert "PASSED ALL TESTS" in output, f"Not all tests passed:\n{output}"

    # Verify no failures
    assert result.returncode == 0, f"Test script returned non-zero exit code:\n{output}"


if __name__ == "__main__":
    # Run pytest when script is executed directly
    sys.exit(pytest.main([__file__, "-v"]))
