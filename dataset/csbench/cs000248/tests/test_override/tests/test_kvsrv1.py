"""
Pytest tests for Key/Value Server implementation.
These tests wrap the Go test command.
The test command is run once and results are cached for all assertions.
"""
import os
import subprocess
import sys
import pytest


# Cached storage for test results
_kv_output = None
_kv_result = None
_lock_output = None
_lock_result = None


def run_kv_test_once():
    """
    Run the KV server Go tests once and cache the result.
    Subsequent calls return the cached result.
    """
    global _kv_output, _kv_result

    if _kv_output is not None:
        return _kv_result

    # Run tests in the kvsrv1 directory
    test_dir = os.path.join(os.path.dirname(__file__), "..", "src", "kvsrv1")

    if not os.path.exists(test_dir):
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    result = subprocess.run(
        ["go", "test", "-v"],
        cwd=test_dir,
        capture_output=True,
        text=True,
        timeout=300
    )

    _kv_output = result.stdout + result.stderr
    _kv_result = result

    return result


def get_kv_test_output():
    """Get the cached KV test output."""
    global _kv_output
    if _kv_output is None:
        run_kv_test_once()
    return _kv_output


def run_lock_test_once():
    """
    Run the Lock Go tests once and cache the result.
    Subsequent calls return the cached result.
    """
    global _lock_output, _lock_result

    if _lock_output is not None:
        return _lock_result

    # Run tests in the kvsrv1/lock directory
    test_dir = os.path.join(os.path.dirname(__file__), "..", "src", "kvsrv1", "lock")

    if not os.path.exists(test_dir):
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    result = subprocess.run(
        ["go", "test", "-v"],
        cwd=test_dir,
        capture_output=True,
        text=True,
        timeout=300
    )

    _lock_output = result.stdout + result.stderr
    _lock_result = result

    return result


def get_lock_test_output():
    """Get the cached Lock test output."""
    global _lock_output
    if _lock_output is None:
        run_lock_test_once()
    return _lock_output


def test_reliable_put():
    """
    Test Put with a single client and a reliable network.
    Verifies basic Put and Get operations.
    """
    output = get_kv_test_output()
    assert "TestReliablePut" in output, "TestReliablePut not found in output"
    assert "--- PASS: TestReliablePut" in output, f"TestReliablePut failed:\n{output}"


def test_put_concurrent_reliable():
    """
    Test many clients putting on same key with reliable network.
    Verifies concurrent access works correctly.
    """
    output = get_kv_test_output()
    assert "TestPutConcurrentReliable" in output, "TestPutConcurrentReliable not found in output"
    assert "--- PASS: TestPutConcurrentReliable" in output, f"TestPutConcurrentReliable failed:\n{output}"


def test_mem_put_many_clients_reliable():
    """
    Test memory usage with many put clients.
    Verifies server doesn't leak memory.
    """
    output = get_kv_test_output()
    assert "TestMemPutManyClientsReliable" in output, "TestMemPutManyClientsReliable not found in output"
    assert "--- PASS: TestMemPutManyClientsReliable" in output, f"TestMemPutManyClientsReliable failed:\n{output}"


def test_unreliable_net():
    """
    Test with one client and unreliable network.
    Verifies client handles dropped messages correctly.
    """
    output = get_kv_test_output()
    assert "TestUnreliableNet" in output, "TestUnreliableNet not found in output"
    assert "--- PASS: TestUnreliableNet" in output, f"TestUnreliableNet failed:\n{output}"


def test_all_kv_tests_passed():
    """
    Test that all KV server tests pass.
    This is a comprehensive test that runs all KV test cases.
    """
    result = run_kv_test_once()
    output = get_kv_test_output()

    # Check for PASS at the end
    assert "PASS" in output, f"KV tests did not pass:\n{output}"

    # Verify no failures
    assert result.returncode == 0, f"KV tests returned non-zero exit code:\n{output}"


def test_one_client_reliable_lock():
    """
    Test lock with one client and reliable network.
    Verifies basic acquire and release operations.
    """
    output = get_lock_test_output()
    assert "TestOneClientReliable" in output, "TestOneClientReliable not found in output"
    assert "--- PASS: TestOneClientReliable" in output, f"TestOneClientReliable failed:\n{output}"


def test_many_clients_reliable_lock():
    """
    Test lock with many clients and reliable network.
    Verifies only one client can hold lock at a time.
    """
    output = get_lock_test_output()
    assert "TestManyClientsReliable" in output, "TestManyClientsReliable not found in output"
    assert "--- PASS: TestManyClientsReliable" in output, f"TestManyClientsReliable failed:\n{output}"


def test_one_client_unreliable_lock():
    """
    Test lock with one client and unreliable network.
    Verifies lock handles network issues correctly.
    """
    output = get_lock_test_output()
    assert "TestOneClientUnreliable" in output, "TestOneClientUnreliable not found in output"
    assert "--- PASS: TestOneClientUnreliable" in output, f"TestOneClientUnreliable failed:\n{output}"


def test_many_clients_unreliable_lock():
    """
    Test lock with many clients and unreliable network.
    Verifies lock works correctly with concurrent access and network issues.
    """
    output = get_lock_test_output()
    assert "TestManyClientsUnreliable" in output, "TestManyClientsUnreliable not found in output"
    assert "--- PASS: TestManyClientsUnreliable" in output, f"TestManyClientsUnreliable failed:\n{output}"


def test_all_lock_tests_passed():
    """
    Test that all Lock tests pass.
    This is a comprehensive test that runs all Lock test cases.
    """
    result = run_lock_test_once()
    output = get_lock_test_output()

    # Check for PASS at the end
    assert "PASS" in output, f"Lock tests did not pass:\n{output}"

    # Verify no failures
    assert result.returncode == 0, f"Lock tests returned non-zero exit code:\n{output}"


if __name__ == "__main__":
    # Run pytest when script is executed directly
    sys.exit(pytest.main([__file__, "-v"]))
