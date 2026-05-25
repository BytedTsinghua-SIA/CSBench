import subprocess
from pathlib import Path


def test_level0():
    cwd = Path(__file__).resolve().parent.parent

    level3 = cwd / "level3.txt"

    assert level3.exists(), f"Missing file: {level3}"

    cmd = "bash -lc 'cat level3.txt | ./hex2raw|./bufbomb -u temp'"
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
    assert "getbuf returned 0x373e31da" in output, (
        "Expected 'getbuf returned 0x373e31da' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )
    assert "VALID" in output, (
        "Expected 'VALID' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )


