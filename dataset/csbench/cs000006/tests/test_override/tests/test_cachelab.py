import re
import subprocess
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parents[1]
INVALID_MISS = 2 ** 31 - 1


def _run_command(command):
    result = subprocess.run(
        command,
        cwd=SRC_DIR,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        pytest.fail(
            f"Command {' '.join(command)} failed with code {result.returncode}.\n"
            f"stdout:\n{stdout}\n"
            f"stderr:\n{stderr}\n"
        )
    return result.stdout


@pytest.fixture(scope="session", autouse=True)
def build_cachelab():
    subprocess.run(["make", "clean"], cwd=SRC_DIR, check=True)
    subprocess.run(["make"], cwd=SRC_DIR, check=True)


def _parse_csim_score(output):
    match = re.search(r"TEST_CSIM_RESULTS=(\d+)", output)
    assert match, "Unable to parse cache simulator output"
    return int(match.group(1))


def _parse_transpose(output):
    match = re.search(r"TEST_TRANS_RESULTS=(\d+):(\d+)", output)
    assert match, "Unable to parse transpose output"
    return int(match.group(1)), int(match.group(2))


def test_cachelab_csim(build_cachelab):
    output = _run_command(["./test-csim"])
    score = _parse_csim_score(output)
    assert score == 27, f"Expected full cache simulator score, got {score}"


def _check_case(m_dim, n_dim, upper):
    output = _run_command(["./test-trans", "-M", m_dim, "-N", n_dim])
    correctness, misses = _parse_transpose(output)
    assert correctness == 1, f"Transpose {m_dim}x{n_dim} failed"
    assert misses != INVALID_MISS, f"Transpose reported invalid misses for {m_dim}x{n_dim}"
    assert misses <= upper, (
        f"Miss count {misses} exceeds expected upper bound {upper} for {m_dim}x{n_dim}"
    )

def test_transpose_32x32():
    _check_case("32", "32", 600)

def test_transpose_64x64():
    _check_case("64", "64", 2000)

def test_transpose_61x67():
    _check_case("61", "67", 3000)