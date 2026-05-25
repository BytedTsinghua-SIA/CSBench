# tests/test_xv6_syscall.py
from gradelib import shell_script, check_time

def test_trace_32_grep(r):
    r.run_qemu(shell_script([
        'trace 32 grep hello README'
    ]))
    r.match(r'^\d+: syscall read -> 1023')
    r.match(r'^\d+: syscall read -> 968')
    r.match(r'^\d+: syscall read -> 235')
    r.match(r'^\d+: syscall read -> 0')

def test_trace_all_grep(r):
    r.run_qemu(shell_script([
        'trace 2147483647 grep hello README'
    ]))
    r.match(r'^\d+: syscall trace -> 0')
    r.match(r'^\d+: syscall exec -> 3')
    r.match(r'^\d+: syscall open -> 3')
    r.match(r'^\d+: syscall read -> 1023')
    r.match(r'^\d+: syscall read -> 968')
    r.match(r'^\d+: syscall read -> 235')
    r.match(r'^\d+: syscall read -> 0')
    r.match(r'^\d+: syscall close -> 0')

def test_trace_nothing(r):
    r.run_qemu(shell_script([
        'grep hello README'
    ]))
    # 原脚本：no=[".* syscall .*"]
    r.match(no=[r'.* syscall .*'])

def test_trace_children(r):
    r.run_qemu(shell_script([
        'trace 2 usertests forkforkfork'
    ]))
    r.match(r'3: syscall fork -> 4')
    r.match(r'^5: syscall fork -> \d+')
    r.match(r'^6: syscall fork -> \d+')
    r.match(r'^\d+: syscall fork -> -1')
    r.match(r'^ALL TESTS PASSED')

def test_sysinfotest(r):
    r.run_qemu(shell_script([
        'sysinfotest'
    ]))
    r.match(r'^sysinfotest: OK', no=[r'.* FAIL .*'])

def test_time():
    check_time()