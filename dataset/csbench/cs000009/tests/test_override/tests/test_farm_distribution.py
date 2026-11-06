import subprocess
from pathlib import Path
import pytest


def test_farm_distributes_work_and_outputs_factorizations():
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "farm"
    assert exe.exists(), f"Missing file: {exe}"

    payload = "\n".join([
        "1001",        # 7 * 11 * 13
        "10001",       # 73 * 137
        "1234567",     # 127 * 9721
    ])
    result = subprocess.run(
        f"printf '{payload}\n' | ./{exe.name}",
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    out = result.stdout or ""
    # Expect multiple factorization lines emitted by workers
    assert result.returncode == 0, f"farm should exit 0.\nOutput:\n{out}"
    lines = [ln for ln in out.splitlines() if ln.strip()]
    result_lines = [ln for ln in lines if "pid:" in ln]
    # We provided 3 inputs, expect at least 3 outputs
    assert len(result_lines) >= 3, (
        f"Expected at least 3 worker result lines, got {len(result_lines)}.\nOutput:\n{out}"
    )
    assert "1001 = 7 * 11 * 13" in out, f"Expected factorization of 1001.\nOutput:\n{out}"
    assert "10001 = 73 * 137" in out, f"Expected factorization of 10001.\nOutput:\n{out}"
    assert "1234567 = 127 * 9721" in out, f"Expected factorization of 1234567.\nOutput:\n{out}"

    # Check concurrency: count distinct PIDs should be at least 2 (often >= min(cpu_count, len(inputs)))
    import re
    pid_re = re.compile(r"\[pid:\s*(\d+)")
    pids = pid_re.findall(out)
    assert len(set(pids)) >= 2, (
        f"Expected results from at least 2 distinct workers, got {len(set(pids))}.\nPIDs: {set(pids)}\nOutput:\n{out}"
    )
