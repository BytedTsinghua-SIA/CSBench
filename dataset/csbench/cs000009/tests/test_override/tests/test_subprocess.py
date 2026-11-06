import subprocess
from pathlib import Path

def test_subprocess():
    """Tests the subprocess-test executable."""
    cwd = Path(__file__).resolve().parent.parent
    executable = cwd / "subprocess-test"

    assert executable.exists(), f"Missing file: {executable}"

    cmd = f"./{executable.name}"
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
    assert result.returncode == 0, (
        f"Expected exit code 0, but got {result.returncode}.\n"
        f"--- output ---\n{output}\n--------------\n"
    )

    expected_words = sorted(["put", "a", "ring", "on", "it"])
    output_words = [word for word in output.strip().split('\n') if word]

    assert output_words == expected_words, (
        f"Output did not match the expected sorted words.\n"
        f"Expected: {expected_words}\n"
        f"Got: {output_words}\n"
        f"--- output ---\n{output}\n--------------\n"
    )