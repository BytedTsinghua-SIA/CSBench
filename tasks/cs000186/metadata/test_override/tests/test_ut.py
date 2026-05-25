import subprocess
from pathlib import Path


def test_arc_replacer_test_passes():
    # Keep consistent style and structure with test_example.py
    cwd = Path(__file__).resolve().parent.parent

    binary = cwd / "build/test/arc_replacer_test"

    assert binary.exists(), f"Missing file: {binary}"

    cmd = f"bash -lc '{binary}'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""

    # Exit code should be 0 when all gtest tests pass
    assert result.returncode == 0, (
        "Expected gtest binary to exit with code 0.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    # Output should include pass markers (gtest versions may vary)
    passed_markers = ["PASSED", "All tests passed", "OK"]
    assert any(m in output for m in passed_markers), (
        "Expected gtest output to indicate all tests passed.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

def test_disk_scheduler_test_passes():
    # Keep consistent style and structure with test_example.py
    cwd = Path(__file__).resolve().parent.parent

    binary = cwd / "build/test/disk_scheduler_test"

    assert binary.exists(), f"Missing file: {binary}"

    cmd = f"bash -lc '{binary}'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""

    # Exit code should be 0 when all gtest tests pass
    assert result.returncode == 0, (
        "Expected gtest binary to exit with code 0.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    # Output should include pass markers (gtest versions may vary)
    passed_markers = ["PASSED", "All tests passed", "OK"]
    assert any(m in output for m in passed_markers), (
        "Expected gtest output to indicate all tests passed.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

def test_buffer_pool_manager_test_passes():
    # Keep consistent style and structure with test_example.py
    cwd = Path(__file__).resolve().parent.parent

    binary = cwd / "build/test/buffer_pool_manager_test"

    assert binary.exists(), f"Missing file: {binary}"

    cmd = f"bash -lc '{binary}'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""

    # Exit code should be 0 when all gtest tests pass
    assert result.returncode == 0, (
        "Expected gtest binary to exit with code 0.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    # Output should include pass markers (gtest versions may vary)
    passed_markers = ["PASSED", "All tests passed", "OK"]
    assert any(m in output for m in passed_markers), (
        "Expected gtest output to indicate all tests passed.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

def test_page_guard_test_passes():
    # Keep consistent style and structure with test_example.py
    cwd = Path(__file__).resolve().parent.parent

    binary = cwd / "build/test/page_guard_test"

    assert binary.exists(), f"Missing file: {binary}"

    cmd = f"bash -lc '{binary}'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""

    # Exit code should be 0 when all gtest tests pass
    assert result.returncode == 0, (
        "Expected gtest binary to exit with code 0.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    # Output should include pass markers (gtest versions may vary)
    passed_markers = ["PASSED", "All tests passed", "OK"]
    assert any(m in output for m in passed_markers), (
        "Expected gtest output to indicate all tests passed.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

