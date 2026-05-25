import subprocess
from pathlib import Path


def test_phase1_defused():
    cwd = Path(__file__).resolve().parent.parent

    bomb = cwd / "bomb"
    ans = cwd / "ans.txt"

    assert bomb.exists(), f"Missing file: {bomb}"
    assert ans.exists(), f"Missing filels: {ans}"

    cmd = "bash -lc './bomb ans.txt'"
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
    assert "Phase 1 defused." in output, (
        "Expected 'Phase 1 defused.' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

