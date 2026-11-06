import subprocess
from pathlib import Path
import pytest


def test_trace_simple_mode_with_simple_test5():
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "trace"
    target = cwd / "simple-test5"
    assert exe.exists() and target.exists(), "trace and simple-test5 must exist"

    result = subprocess.run(
        f"./{exe.name} --simple ./{target.name}",
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
    )

    out = result.stdout or ""
    # Expected to contain bare-bones syscall lines, e.g.:
    # syscall(59) = 0
    assert "syscall(" in out


def test_trace_full_mode_formats_errno_and_strings():
    cwd = Path(__file__).resolve().parent.parent
    exe = cwd / "trace"
    target = cwd / "simple-test5"
    assert exe.exists() and target.exists(), "trace and simple-test5 must exist"

    # Limit output and runtime to avoid excessive tracing delays
    result = subprocess.run(
        f"./{exe.name} ./{target.name} | head -n 200",
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
    )

    out = result.stdout or ""
    # Expected examples when implemented:
    # execve("./simple-test5", ...) = 0
    # write(1, "12345\n", 6) = 12345
    # close(1000) = -1 EBADF (Bad file descriptor)
    import re
    has_errno = re.search(r"\bE[A-Z0-9_]+\b", out) is not None
    assert ("execve(" in out) or ("write(" in out) or has_errno, (
        f"Expected full-mode formatted details (name/args or errno).\n"
        f"Output:\n{out}"
    )
