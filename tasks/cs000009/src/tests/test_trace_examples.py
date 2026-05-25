import subprocess
from pathlib import Path
import pytest
import re


@pytest.mark.parametrize("target", [
    "simple-test1",
    "simple-test2",
    "simple-test3",
    "simple-test4",
])
def test_trace_simple_mode_on_examples(target):
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "trace"
    t = cwd / target
    assert exe.exists() and t.exists(), f"Missing executable(s): {exe}, {t}"

    # Limit output to keep runs fast and robust across distros
    cmd = f"./{exe.name} --simple ./{t.name} | head -n 100"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
    )

    out = result.stdout or ""
    assert "syscall(" in out, (
        f"Expected bare syscall lines in simple mode.\nOutput:\n{out}"
    )


@pytest.mark.parametrize("target", [
    "simple-test1",
    "simple-test2",
    "simple-test3",
    "simple-test4",
])
def test_trace_full_mode_on_examples(target):
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "trace"
    t = cwd / target
    assert exe.exists() and t.exists(), f"Missing executable(s): {exe}, {t}"

    cmd = f"./{exe.name} ./{t.name} | head -n 200"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
    )

    out = result.stdout or ""
    has_errno = re.search(r"\bE[A-Z0-9_]+\b", out) is not None
    assert ("execve(" in out) or ("write(" in out) or has_errno, (
        f"Expected formatted full-mode output (name/args or errno).\nOutput:\n{out}"
    )

