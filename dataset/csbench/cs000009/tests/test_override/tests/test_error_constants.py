import subprocess
from pathlib import Path


def test_errno_constants_mapping_contains_ENOENT():
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "trace-error-constants-test"
    assert exe.exists(), f"Missing file: {exe}"

    result = subprocess.run(
        f"./{exe.name}",
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""
    # Expect that ENOENT (2) appears in the parsed mapping on Ubuntu images.
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\nOutput:\n{output}"
    assert "2 -> ENOENT" in output, (
        "Expected ENOENT mapping to be present in error constants output.\n"
        f"Output:\n{output}"
    )

