#!/usr/bin/env python3
"""
Pytest tests for xv6 net lab.
Replicates the grade-lab-net grading script.
"""
import sys
import os
import re
import subprocess
import time

# Add the lab-net directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lab-net'))

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
    # Change to lab-net directory where Makefile resides
    xv6_dir = os.path.join(os.path.dirname(__file__), '..', 'lab-net')
    original_cwd = os.getcwd()
    os.chdir(xv6_dir)
    try:
        gradelib.make()
        gradelib.reset_fs()
        yield
    finally:
        os.chdir(original_cwd)


# Fixture that runs nettests with server and returns the Runner with output
@pytest.fixture(scope='module')
def nettests_output():
    """Run nettests via QEMU with server subprocess and return the Runner instance."""
    # Start the echo server
    xv6_dir = os.path.join(os.path.dirname(__file__), '..', 'lab-net')
    original_cwd = os.getcwd()
    os.chdir(xv6_dir)
    try:
        # Start server subprocess
        server = subprocess.Popen(["make", "server"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Give server a moment to bind
        time.sleep(0.5)
        
        r = gradelib.Runner()
        r.run_qemu(gradelib.shell_script(['nettests']), timeout=30)
        
        # Terminate server
        server.terminate()
        server.communicate()
        
        return r
    finally:
        os.chdir(original_cwd)


# Test functions
def test_nettest_ping(nettests_output):
    """Test nettests: ping"""
    nettests_output.match('^testing ping: OK$')

def test_nettest_single_process(nettests_output):
    """Test nettests: single process"""
    nettests_output.match('^testing single-process pings: OK$')

def test_nettest_multi_process(nettests_output):
    """Test nettests: multi-process"""
    nettests_output.match('^testing multi-process pings: OK$')

def test_nettest_dns(nettests_output):
    """Test nettests: DNS"""
    nettests_output.match('^DNS OK$')

def test_time():
    """Test time command"""
    gradelib.check_time()