# tests/test_xv6_traps.py
import os
import re
import subprocess
import pytest
from gradelib import shell_script, check_answers, check_time, assert_equal

BACKTRACE_RE = r"^(0x000000008[0-9a-f]+)"

def addr2line():
    for f in ['riscv64-unknown-elf-addr2line', 'riscv64-linux-gnu-addr2line', 'addr2line']:
        try:
            subprocess.Popen([f], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).communicate()
            return f
        except OSError:
            continue
    raise AssertionError('Cannot find the addr2line program')

def test_answers_traps():
    check_answers("answers-traps.txt")

def test_backtrace(r):
    r.run_qemu(shell_script(['bttest']))
    a2l = addr2line()
    matches = re.findall(BACKTRACE_RE, r.qemu.output, re.MULTILINE)
    assert_equal(len(matches), 3)
    files = ['sysproc.c', 'syscall.c', 'trap.c']
    for f, m in zip(files, matches):
        result = subprocess.run([a2l, '-e', 'kernel/kernel', m], stdout=subprocess.PIPE)
        assert f in result.stdout.decode("utf-8")

@pytest.fixture(scope="module")
def alarm_output(r):
    r.run_qemu(shell_script(['alarmtest']))
    return r.qemu.output

def test_alarm_test0(alarm_output):
    assert re.search(r'^test0 passed$', alarm_output, re.M)

def test_alarm_test1(alarm_output):
    assert re.search(r'^\.*test1 passed$', alarm_output, re.M)

def test_alarm_test2(alarm_output):
    assert re.search(r'^\.*test2 passed$', alarm_output, re.M)

def test_usertests(r):
    r.run_qemu(shell_script(['usertests']), timeout=300)
    r.match(r'^ALL TESTS PASSED$')

def test_time():
    check_time()