import subprocess
from pathlib import Path


def test_level0():
    cwd = Path(__file__).resolve().parent.parent

    level4 = cwd / "level4.txt"

    assert level4.exists(), f"Missing file: {level4}"

    cmd = "bash -lc 'cat level4.txt | ./hex2raw -n|./bufbomb -n -u temp'"
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
    assert "getbufn returned 0x373e31da" in output, (
        "Expected 'getbufn returned 0x373e31da' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )
    assert "VALID" in output, (
        "Expected 'VALID' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )


