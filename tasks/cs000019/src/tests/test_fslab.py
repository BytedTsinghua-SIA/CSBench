# tests/test_xv6_fs.py
import re
import pytest
from gradelib import shell_script, assert_lines_match, check_time

def _run_(r, cmd: str, timeout: int):
    r.run_qemu(shell_script([cmd]), timeout=timeout)
    out = r.qemu.output
    return out

@pytest.mark.slow
def test_bigfile(r):
    _run_(r, "bigfile", timeout=300)
    r.match(r"^wrote 65803 blocks$", r"^bigfile done; ok$")

@pytest.fixture(scope="module")
def symlink_output(r):
    out = _run_(r, "symlinktest", timeout=30)
    return out

@pytest.mark.parametrize("pattern", [
    r"^test symlinks: ok$",
    r"^test concurrent symlinks: ok$",
])
def test_symlink_ok(symlink_output, pattern):
    assert_lines_match(symlink_output, pattern)

@pytest.mark.slow
def test_usertests(r):
    _run_(r, "usertests", timeout=600)
    r.match(r"^ALL TESTS PASSED$")

def test_time():
    check_time()