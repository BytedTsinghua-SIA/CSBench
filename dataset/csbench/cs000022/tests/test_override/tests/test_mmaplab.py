# tests/test_xv6_mmap.py
import pytest
from gradelib import shell_script, assert_lines_match, check_time

@pytest.fixture(scope="module")
def mmap_output(r):
    r.run_qemu(shell_script(['mmaptest']), timeout=180)
    return r.qemu.output

def test_mmap_f(mmap_output):
    assert_lines_match(mmap_output, r'^test mmap f: OK$')

def test_mmap_private(mmap_output):
    assert_lines_match(mmap_output, r'^test mmap private: OK$')

def test_mmap_read_only(mmap_output):
    assert_lines_match(mmap_output, r'^test mmap read-only: OK$')

def test_mmap_read_write(mmap_output):
    assert_lines_match(mmap_output, r'^test mmap read/write: OK$')

def test_mmap_dirty(mmap_output):
    assert_lines_match(mmap_output, r'^test mmap dirty: OK$')

def test_not_mapped_unmap(mmap_output):
    assert_lines_match(mmap_output, r'^test not-mapped unmap: OK$')

def test_mmap_two_files(mmap_output):
    assert_lines_match(mmap_output, r'^test mmap two files: OK$')

def test_fork_test(mmap_output):
    assert_lines_match(mmap_output, r'^fork_test OK$')

def test_usertests(r):
    r.run_qemu(shell_script(['usertests']), timeout=420)
    r.match(r'^ALL TESTS PASSED$')

def test_time():
    check_time()