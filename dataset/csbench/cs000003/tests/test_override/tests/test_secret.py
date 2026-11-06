import subprocess
from pathlib import Path


def test_phase_secret_defused():
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
    assert "Curses, you've found the secret phase!" in output, (
        "Expected 'Curses, you've found the secret phase!' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )
    assert "You've defused the secret stage!" in output, (
        "Expected 'You've defused the secret stage!' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )
