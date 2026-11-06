import subprocess
from pathlib import Path
import re

def test_partA():
    cwd1 = Path(__file__).resolve().parent.parent
    cwd = cwd1 / "sim/misc"
    sum = cwd / "sum.ys"
    rsum = cwd / "rsum.ys"
    copy = cwd / "copy.ys"

    assert sum.exists(), f"Missing file: {sum}"
    assert rsum.exists(), f"Missing filels: {rsum}"
    assert copy.exists(), f"Missing file: {copy}"

    cmd = "bash -lc 'cd sim && make clean; make'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    cmd = "bash -lc './yas ./sum.ys && ./yis ./sum.yo'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    pattern = r"%rax:\s*0x0000000000000000\s*0x0000000000000cba"
    output = result.stdout or ""
    assert re.search(pattern, output)

    cmd = "bash -lc './yas ./rsum.ys && ./yis ./rsum.yo'"
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
    assert re.search(pattern, output)

    cmd = "bash -lc './yas ./copy.ys && ./yis ./copy.yo'"
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
    assert re.search(pattern, output)