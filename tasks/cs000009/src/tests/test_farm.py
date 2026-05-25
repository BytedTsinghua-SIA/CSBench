import subprocess
from pathlib import Path


def test_farm_runs_and_processes_inputs():
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "farm"
    assert exe.exists(), f"Missing file: {exe}"

    # Provide small inputs; expect worker outputs with pid info and correct factorization lines.
    payload = "\n".join(["1", "2", "3"]) + "\n"
    result = subprocess.run(
        f"printf '{payload}' | ./{exe.name}",
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""
    assert result.returncode == 0, (
        f"farm should exit 0.\nOutput:\n{output}"
    )
    # Expect three worker outputs (one per input line)
    lines = [ln for ln in output.splitlines() if ln.strip()]
    result_lines = [ln for ln in lines if "pid:" in ln]
    assert len(result_lines) >= 3, (
        f"Expected at least 3 worker result lines, got {len(result_lines)}.\nOutput:\n{output}"
    )
    # Check that factorization strings for 1,2,3 appear
    assert "1 = 1" in output, f"Expected factorization for 1.\nOutput:\n{output}"
    assert "2 = 2" in output, f"Expected factorization for 2.\nOutput:\n{output}"
    assert "3 = 3" in output, f"Expected factorization for 3.\nOutput:\n{output}"
