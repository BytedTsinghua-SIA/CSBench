import subprocess
import re
from pathlib import Path

def test_partC():
    cwd1 = Path(__file__).resolve().parent.parent
    cwd2 = cwd1/ "sim/pipe"

    cmd = "bash -lc 'make drivers'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd2),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    cmd = "bash -lc 'make psim VERSION=full'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd2),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


    cmd = "bash -lc './correctness.pl'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd2),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""
    assert "68/68 pass correctness test" in output, (
        "Expected '68/68 pass correctness test' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    cmd = "bash -lc './benchmark.pl'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd2),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""

    match = re.search(r"Average CPE\s+([\d.]+)", output)
    assert match, (
        "Failed to match score.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )
    cpe = float(match.group(1))
    assert cpe <= 9.00, (
        f"Expected benchmark cpe <= 9.00, got {cpe}.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )