import pytest
from conftest import run_program

@pytest.mark.parametrize("threads", [1, 32])
def test_program_runs(quake_omp, quake_input, threads):
    out = run_program(quake_omp, threads, quake_input)
    assert len(out) > 0
