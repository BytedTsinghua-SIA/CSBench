from _simpletest_helper import run_group


def test_heap_pqueue(tmp_path):
    assert run_group(tmp_path, "HeapPQueue.cpp") == 0
