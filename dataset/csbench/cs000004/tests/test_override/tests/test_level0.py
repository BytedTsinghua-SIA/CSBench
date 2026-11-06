import subprocess
from pathlib import Path


def test_level0():
    cwd = Path(__file__).resolve().parent.parent

    level0 = cwd / "level0.txt"

    assert level0.exists(), f"Missing file: {level0}"

    cmd = "bash -lc 'cat level0.txt | ./hex2raw|./bufbomb -u temp'"
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
    assert "You called smoke()" in output, (
        "Expected 'You called smoke()' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )
    assert "VALID" in output, (
        "Expected 'VALID' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )


