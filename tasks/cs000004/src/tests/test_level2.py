import subprocess
from pathlib import Path


def test_level0():
    cwd = Path(__file__).resolve().parent.parent

    level2 = cwd / "level2.txt"

    assert level2.exists(), f"Missing file: {level2}"

    cmd = "bash -lc 'cat level2.txt | ./hex2raw|./bufbomb -u temp'"
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
    assert "You set global_value to 0x373e31da" in output, (
        "Expected 'You set global_value to 0x373e31da' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )
    assert "VALID" in output, (
        "Expected 'VALID' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )


