import subprocess
from pathlib import Path


def test_trace_no_target_prints_hint():
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "trace"
    assert exe.exists(), f"Missing file: {exe}"

    # No target: should print friendly message and exit 0
    result = subprocess.run(
        f"./{exe.name}",
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
    assert "Nothing to trace... exiting." in (result.stdout or ""), (
        "Expected hint message when no target is provided.\n"
        f"Output:\n{result.stdout}"
    )


def test_trace_simple_flag_only():
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "trace"
    assert exe.exists(), f"Missing file: {exe}"

    result = subprocess.run(
        f"./{exe.name} --simple",
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Still prints the same hint line (no target provided)
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}"
    assert "Nothing to trace... exiting." in (result.stdout or ""), (
        "Expected hint message when only flags are supplied.\n"
        f"Output:\n{result.stdout}"
    )

