from hashall import *
from hashbig import *
from sol import problem_2a, problem_2c, problem_4b, problem_3a, problem_3b, problem_3c, problem_3d, problem_3e

import traceback

def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    import signal
    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    finally:
        signal.alarm(0)

    return result

def _close(a, b, rel=1e-9, abs_tol=1e-12):
    return abs(a - b) <= max(abs_tol, rel * max(abs(a), abs(b)))

def test_2a():
    result = timeout(problem_2a,timeout_duration = 5*60)
    
    if(isinstance(result, str)):
        result = result.encode("ascii")

    target = "e048903a3248"

    if toy_hash(result).hex() != target:
        raise Exception(f"toy_hash(password) outputs {toy_hash(result).hex()}, not {target}")


def test_2c():
    data_hash = set()

    with open("hashes.txt",'r') as data_file:
            for line in data_file:
                data_hash.add(line.strip())

    
    result = timeout(problem_2c,timeout_duration =10*60)


    if(isinstance(result, str)):
        result = result.encode("ascii")
  

    if toy_hash(result).hex() not in data_hash:
        raise Exception(f"toy_hash(password) = {toy_hash(result).hex()} is not found in the text file of hashes!")

def test_3a():
    p_one_bin = problem_3a(5, 1)
    if not _close(p_one_bin, 1):
        raise Exception()

    p_b_small = problem_3a(1, 7)
    p_b_large = problem_3a(9, 7)
    if not _close(p_b_small, p_b_large):
        raise Exception()

    p_n2 = problem_3a(4, 2)
    p_n5 = problem_3a(4, 5)
    if not _close(p_n2 * 2, p_n5 * 5):
        raise Exception()

    if not (0 <= p_n2 <= 1 and 0 <= p_n5 <= 1):
        raise Exception()

def test_3b():
    p_one_bin = problem_3b(2, 1)
    if not _close(p_one_bin, 1):
        raise Exception()

    p_b_small = problem_3b(2, 3)
    p_b_large = problem_3b(7, 3)
    if not _close(p_b_small, p_b_large):
        raise Exception()

    p_n2 = problem_3b(2, 2)
    p_n4 = problem_3b(2, 4)
    if not _close(p_n2 * (2 ** 2), p_n4 * (4 ** 2)):
        raise Exception()

    if not (0 <= p_n2 <= 1 and 0 <= p_n4 <= 1):
        raise Exception()

def test_3c():
    if not _close(problem_3c(0), 0):
        raise Exception()
    if not _close(problem_3c(1), 0):
        raise Exception()

    for b in (1, 2, 5, 10):
        if not _close(problem_3c(b + 1) - problem_3c(b), b):
            raise Exception()

def test_3d():
    if not _close(problem_3d(0, 5), 0):
        raise Exception()
    if not _close(problem_3d(1, 5), 0):
        raise Exception()

    p_n2 = problem_3d(6, 2)
    p_n5 = problem_3d(6, 5)
    if not _close(p_n2 * 2, p_n5 * 5):
        raise Exception()

    if not _close(problem_3d(6, 1), problem_3c(6)):
        raise Exception()

def test_3e():
    if not _close(problem_3e(1, 4), 0):
        raise Exception()

    l_val = 6
    if not _close(problem_3e(l_val, 1), problem_3d(l_val, 2)):
        raise Exception()
    if not _close(problem_3e(l_val, 3), problem_3d(l_val, 8)):
        raise Exception()

    p_n2 = problem_3e(l_val, 2)
    p_n5 = problem_3e(l_val, 5)
    if not _close(p_n2 * (2 ** 2), p_n5 * (2 ** 5)):
        raise Exception()

def test_4b():
    a,b = timeout(problem_4b,timeout_duration =20*60)
    
    if a == b:
        raise Exception(f"colliding pre-images can not be equal! {a} == {b}")

    if H(a) !=  H(b):
        raise Exception(f"H({a}) = {H(a).hex()} != H({b}) = {H(b).hex()}")

def test_questions():
    file = open("questions.txt", "r")
    data = file.read()
    number_of_characters = len(data)

    if number_of_characters < 500:
        raise Exception("questions.txt not answered!")

checks = {
    "2a": test_2a,
    "2c": test_2c,
    "3a": test_3a,
    "3b": test_3b,
    "3c": test_3c,
    "3d": test_3d,
    "3e": test_3e,
    "4b": test_4b,
    "questions": test_questions
}

if __name__ == '__main__':
    for n, f in checks.items():
        try:
            f()
            print("%s: pass" % n)
        except:
            traceback.print_exc()
            print("%s: fail" % n)
