#!/usr/bin/env python3
"""
Pytest tests for xv6 cow lab.
Replicates the grade-lab-cow grading script.
"""
import sys
import os
import re

# Add the xv6-labs-2021 directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'xv6-labs-2021'))

import gradelib

# Set global options that gradelib expects
gradelib.options = gradelib.OptionParser().parse_args([])[0]
gradelib.options.color = 'never'
gradelib.options.verbose = False

import pytest

# Session-scoped fixture to build xv6 and reset filesystem
@pytest.fixture(scope='session', autouse=True)
def build_and_reset():
    """Run make and reset_fs once per test session."""
    # Change to xv6 directory where Makefile resides
    xv6_dir = os.path.join(os.path.dirname(__file__), '..', 'xv6-labs-2021')
    original_cwd = os.getcwd()
    os.chdir(xv6_dir)
    try:
        gradelib.make()
        gradelib.reset_fs()
        yield
    finally:
        os.chdir(original_cwd)

# Fixture that runs cowtest and returns the Runner with output
@pytest.fixture(scope='module')
def cowtest_output():
    """Run cowtest via QEMU and return the Runner instance."""
    r = gradelib.Runner()
    r.run_qemu(gradelib.shell_script(['cowtest']))
    return r

# Fixture that runs usertests and returns the Runner with output
@pytest.fixture(scope='module')
def usertests_output():
    """Run usertests via QEMU and return the Runner instance."""
    r = gradelib.Runner()
    r.run_qemu(gradelib.shell_script(['usertests']), timeout=300)
    return r

# Test functions

def test_cowtest_runs(cowtest_output):
    """Ensure cowtest runs without crashing."""
    # The fixture already runs cowtest; if it fails, the fixture would raise.
    # We can add a simple check that output contains something.
    assert len(cowtest_output.qemu.output) > 0

def test_simple(cowtest_output):
    """Check that simple: ok appears twice."""
    matches = re.findall(r"^simple: ok$", cowtest_output.qemu.output, re.MULTILINE)
    assert len(matches) == 2, f"Expected 2 appearances of 'simple: ok', got {len(matches)}"

def test_three(cowtest_output):
    """Check that three: ok appears three times."""
    matches = re.findall(r"^three: ok$", cowtest_output.qemu.output, re.MULTILINE)
    assert len(matches) == 3, f"Expected 3 appearances of 'three: ok', got {len(matches)}"

def test_file(cowtest_output):
    """Check that file: ok appears."""
    cowtest_output.match(r'^file: ok$')

def test_usertests_runs(usertests_output):
    """Ensure usertests runs and passes."""
    usertests_output.match(r'^ALL TESTS PASSED$')

def test_usertests_copyin(usertests_output):
    """Check copyin test passes."""
    output = usertests_output.qemu.output
    # Look for pattern: test copyin: ... OK followed by test copyout
    if not re.search(r'\ntest copyin: [\s\S]*?OK\ntest copyout', output):
        raise AssertionError('Failed copyin')

def test_usertests_copyout(usertests_output):
    """Check copyout test passes."""
    output = usertests_output.qemu.output
    if not re.search(r'\ntest copyout: [\s\S]*?OK\ntest copyinstr1', output):
        raise AssertionError('Failed copyout')

def test_usertests_all(usertests_output):
    """Check that all tests passed."""
    usertests_output.match(r'^ALL TESTS PASSED$')

def test_time():
    """Check time.txt exists and contains integer."""
    gradelib.check_time()

# Optional: score calculation (not needed for pytest)
# We can keep the original point values as metadata but not used.
