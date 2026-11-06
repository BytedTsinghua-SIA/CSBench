import subprocess
from pathlib import Path


def test_level0():
    cwd = Path(__file__).resolve().parent.parent

    level1 = cwd / "level1.txt"

    assert level1.exists(), f"Missing file: {level1}"

    cmd = "bash -lc 'cat level1.txt | ./hex2raw|./bufbomb -u temp'"
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
    assert "You called fizz" in output, (
        "Expected 'You called fizz' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )
    assert "VALID" in output, (
        "Expected 'VALID' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )


