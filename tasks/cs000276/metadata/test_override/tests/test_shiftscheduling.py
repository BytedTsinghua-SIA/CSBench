from _simpletest_helper import run_group


def test_shiftscheduling(tmp_path):
    assert run_group(tmp_path, "ShiftScheduling.cpp") == 0
