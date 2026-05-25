import os
import subprocess
import time
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, ".")

SERIAL_BIN = os.path.join(SRC_DIR, "quake_serial")
OMP_BIN = os.path.join(SRC_DIR, "quake_omp")
INPUT_SHORT = os.path.join(SRC_DIR, "quake.in.short")
INPUT = os.path.join(SRC_DIR, "quake.in")


# ========================
# Build once per test run
# ========================
@pytest.fixture(scope="session", autouse=True)
def build_binaries():
    print("\n[pytest] Rebuilding binaries...")
    subprocess.check_call(["make", "clean"], cwd=SRC_DIR)
    subprocess.check_call(["make"], cwd=SRC_DIR)
    yield


# ========================
# Path fixtures
# ========================
@pytest.fixture
def quake_serial():
    return SERIAL_BIN


@pytest.fixture
def quake_omp():
    return OMP_BIN


@pytest.fixture
def quake_input():
    return INPUT


# ========================
# Helpers
# ========================
def run_program(binary, threads, input_file):
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(threads)

    result = subprocess.run(
        [binary],
        stdin=open(input_file),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        check=True,
    )
    return result.stdout


def time_program(binary, threads, input_file):
    start = time.perf_counter()
    run_program(binary, threads, input_file)
    return time.perf_counter() - start
