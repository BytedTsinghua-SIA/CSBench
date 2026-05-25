# tests/test_xv6_threadlab.py
import re
import subprocess
from gradelib import shell_script, check_answers, check_time

def test_uthread(r):
    r.run_qemu(shell_script(['uthread']))
    expected = ['thread_a started', 'thread_b started', 'thread_c started']
    expected.extend([f'thread_{tid} {n}' for n in range(100) for tid in ('c', 'a', 'b')])
    expected.extend(['thread_c: exit after 100', 'thread_a: exit after 100', 'thread_b: exit after 100'])
    expected.append('thread_schedule: no runnable threads')

    pattern = '\n'.join(expected)
    if not re.findall(pattern, r.qemu.output, re.M):
        raise AssertionError('Output does not match expected output')

def test_answers_thread():
    check_answers("answers-thread.txt")

def test_ph_safe():
    subprocess.run(['make', 'ph'], check=True)
    result = subprocess.run(['./ph', '2'], stdout=subprocess.PIPE, check=True)
    out = result.stdout.decode('utf-8')
    matches = re.findall(r'^\d+: (\d+) keys missing$', out, re.MULTILINE)
    assert len(matches) == 2
    assert int(matches[0]) == 0
    assert int(matches[1]) == 0

def test_ph_fast():
    subprocess.run(['make', 'ph'], check=True)

    # 两线程
    res2 = subprocess.run(['./ph', '2'], stdout=subprocess.PIPE, check=True)
    out2 = res2.stdout.decode('utf-8')
    rate2 = re.findall(r' (\d+) puts.second$', out2, re.MULTILINE)
    assert len(rate2) == 1

    # 单线程
    res1 = subprocess.run(['./ph', '1'], stdout=subprocess.PIPE, check=True)
    out1 = res1.stdout.decode('utf-8')
    rate1 = re.findall(r' (\d+) puts.second$', out1, re.MULTILINE)
    assert len(rate1) == 1

    rate1 = float(rate1[0])
    rate2 = float(rate2[0])
    # 至少 1.25x 加速
    assert rate2 >= 1.25 * rate1, 'Parallel put() speedup is less than 1.25x'

def test_barrier():
    subprocess.run(['make', 'barrier'], check=True)
    res = subprocess.run(['./barrier', '2'], stdout=subprocess.PIPE, check=True)
    out = res.stdout.decode('utf-8').strip()
    assert re.match(r'^OK; passed$', out), 'Barrier failed'

def test_time():
    check_time()