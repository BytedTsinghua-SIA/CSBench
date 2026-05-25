import pytest
from conftest import run_program

THREADS = [1, 2, 4, 8, 16, 32]


def normalize_output(output: str) -> str:
    """
    Remove lines that are allowed to differ, e.g. numthreads
    """
    lines = output.strip().splitlines()
    filtered = [
        line for line in lines
        if not line.lower().startswith("numthreads")
    ]
    return "\n".join(filtered)


@pytest.mark.parametrize("threads", THREADS)
def test_output_matches_serial(
    quake_serial, quake_omp, quake_input, threads
):
    serial_out = run_program(quake_serial, 1, quake_input)
    omp_out = run_program(quake_omp, threads, quake_input)

    serial_norm = normalize_output(serial_out)
    omp_norm = normalize_output(omp_out)

    assert omp_norm == serial_norm, f"Output mismatch at {threads} threads"
