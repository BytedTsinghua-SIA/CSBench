import subprocess
from pathlib import Path

def test_partB():
    cwd1 = Path(__file__).resolve().parent.parent
    cwd2 = cwd1/ "sim/seq"
    cwd3 = cwd1/ "sim/y86-code"
    cwd4 = cwd1/ "sim/ptest"

    cmd = "bash -lc 'make VERSION=full'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd1),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    cmd = "bash -lc './ssim -t ../y86-code/asumi.yo'"
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
    assert "ISA Check Succeeds" in output, (
        "Expected 'ISA Check Succeeds' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    cmd = "bash -lc 'make testssim'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd3),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""
    expected_names = [
        "asum", "asumr", "cjr", "j-cc", "poptest", "prog1", "prog2", "prog3",
        "prog4", "prog5", "prog6", "prog7", "prog8",
        "pushquestion", "pushtest", "ret-hazard"
    ]
    for name in expected_names:
        expected_string = name + ".seq:" + "ISA Check Succeeds"
        assert expected_string in output, (
            "Expected '"+ expected_string + "' in program output.\n"
            f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
        )


    cmd = "bash -lc 'make SIM=../seq/ssim'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd4),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""
    assert "All 600 ISA Checks Succeed" in output, (
        "Expected 'All 600 ISA Checks Succeed' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    cmd = "bash -lc 'make SIM=../seq/ssim TFLAGS=-i'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd4),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""
    assert "All 756 ISA Checks Succeed" in output, (
        "Expected 'All 756 ISA Checks Succeed' in program output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )