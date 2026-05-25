#!/usr/bin/env python3
"""
Pytest tests for xv6 cow lab.
Replicates the grade-lab-cow grading script.
"""
import sys
import os
import re

# Add the lab-lock directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lab-lock'))

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
    # Change to lab-lock directory where Makefile resides
    xv6_dir = os.path.join(os.path.dirname(__file__), '..', 'lab-lock')
    original_cwd = os.getcwd()
    os.chdir(xv6_dir)
    try:
        gradelib.make()
        gradelib.reset_fs()
        yield
    finally:
        os.chdir(original_cwd)
        
        
# Fixture that runs kalloctest and returns the Runner with output
@pytest.fixture(scope='module')
def kalloctest_output():
    """Run kalloctest via QEMU and return the Runner instance."""
    r = gradelib.Runner()
    r.run_qemu(gradelib.shell_script(['kalloctest']), timeout=200)
    return r

# Fixture that runs bcachetest and returns the Runner with output
@pytest.fixture(scope='module')
def bcachetest_output():
    """Run bcachetest via QEMU and return the Runner instance."""
    r = gradelib.Runner()
    r.run_qemu(gradelib.shell_script(['bcachetest']), timeout=90)
    return r

# Fixture that runs usertests and returns the Runner with output
@pytest.fixture(scope='module')
def usertests_output():
    """Run usertests via QEMU and return the Runner instance."""
    r = gradelib.Runner()
    r.run_qemu(gradelib.shell_script(['usertests']), timeout=300)
    return r

# Test functions
def test_kalloctest_test1(kalloctest_output):
    """Test kalloctest: test1"""
    kalloctest_output.match('^test1 OK$')
    
def test_kalloctest_test2(kalloctest_output):
    """Test kalloctest: test2"""
    kalloctest_output.match('^test2 OK$')
    
def test_sbrkmuch():
    """Test sbrkmuch"""
    r = gradelib.Runner()
    r.run_qemu(gradelib.shell_script(['usertests sbrkmuch']), timeout=90)
    r.match('^ALL TESTS PASSED$')
    
def test_bcachetest_test0(bcachetest_output):
    """Test bcachetest: test0"""
    bcachetest_output.match('^test0: OK$')
    
def test_bcachetest_test1(bcachetest_output):
    """Test bcachetest: test1"""
    bcachetest_output.match('^test1 OK$')
    
def test_usertests(usertests_output):
    """Test usertests"""
    usertests_output.match('^ALL TESTS PASSED$')
    
def test_time():
    """Test time command"""
    gradelib.check_time()