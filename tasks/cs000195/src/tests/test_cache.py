"""
Unit Tests for L2 Cache and DRAM
Tests core functionality only
Corresponds to test_cache.c - 12 tests total
"""

import os
import subprocess
import pytest
import re


# Get the directory containing this test file
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(TEST_DIR)
TEST_CACHE_EXE = os.path.join(SRC_DIR, "test_cache")


def run_test_cache():
    """Run test_cache executable and parse output"""
    if not os.path.exists(TEST_CACHE_EXE):
        pytest.skip(f"test_cache executable not found at {TEST_CACHE_EXE}")

    try:
        result = subprocess.run(
            [TEST_CACHE_EXE], cwd=SRC_DIR, capture_output=True, text=True, timeout=10
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        pytest.fail("test_cache timed out")
    except Exception as e:
        pytest.fail(f"Failed to run test_cache: {e}")


def parse_test_output(output):
    """Parse test output and return dict of test results"""
    results = {}
    lines = output.split("\n")

    for line in lines:
        if line.startswith("PASS:"):
            test_name = line.replace("PASS:", "").strip()
            results[test_name] = True
        elif line.startswith("FAIL:"):
            test_name = line.replace("FAIL:", "").strip()
            results[test_name] = False

    return results


def get_test_results():
    """Get test results from running test_cache"""
    stdout, stderr, returncode = run_test_cache()
    results = parse_test_output(stdout)
    return results, stdout, stderr, returncode


@pytest.fixture(scope="module")
def test_results():
    """Run test_cache once and cache results for all tests"""
    results, stdout, stderr, returncode = get_test_results()
    return {
        "results": results,
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
    }


def test_cache_init(test_results):
    """Test 1: Cache initialization"""
    test_name = "Cache initialization"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_get_cache_block_addr(test_results):
    """Test 2: Address decomposition - cache block address"""
    test_name = "Get cache block address"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_get_l2_set_index(test_results):
    """Test 3: Address decomposition - L2 set index"""
    test_name = "Get L2 set index"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_get_dram_bank(test_results):
    """Test 4: Address decomposition - DRAM bank"""
    test_name = "Get DRAM bank"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_get_dram_row(test_results):
    """Test 5: Address decomposition - DRAM row"""
    test_name = "Get DRAM row"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_l2_cache_miss_mshr(test_results):
    """Test 6: L2 cache miss - MSHR allocation"""
    test_name = "L2 cache miss - MSHR allocation"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_l2_cache_hit(test_results):
    """Test 7: L2 cache hit - immediate return"""
    test_name = "L2 cache hit - immediate return"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_lru_replacement(test_results):
    """Test 8: LRU replacement"""
    test_name = "LRU replacement"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_mru_promotion(test_results):
    """Test 9: MRU promotion"""
    test_name = "MRU promotion"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_memory_controller_scheduling(test_results):
    """Test 10: Memory controller - request scheduling"""
    test_name = "Memory controller - request scheduling"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_mshr_limit(test_results):
    """Test 11: MSHR limit"""
    test_name = "MSHR limit"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_cache_write(test_results):
    """Test 12: Write to cache"""
    test_name = "Cache write"
    assert (
        test_name in test_results["results"]
    ), f"Test '{test_name}' not found in output"
    assert test_results["results"][test_name], f"Test '{test_name}' failed"


def test_all_tests_passed(test_results):
    """Verify all tests passed and check summary"""
    stdout = test_results["stdout"]

    # Check for test summary
    summary_match = re.search(
        r"Passed:\s+(\d+)\s+Failed:\s+(\d+)\s+Total:\s+(\d+)", stdout
    )
    if summary_match:
        passed = int(summary_match.group(1))
        failed = int(summary_match.group(2))
        total = int(summary_match.group(3))

        assert failed == 0, f"Some tests failed: {failed} failed out of {total}"
        assert passed == total, f"Not all tests passed: {passed}/{total}"
        assert total == 12, f"Expected 12 tests, found {total}"

    # Verify return code
    assert test_results["returncode"] == 0, "test_cache returned non-zero exit code"
