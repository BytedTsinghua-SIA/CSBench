from _simpletest_helper import run_group


def test_humanpyramids(tmp_path):
    assert run_group(tmp_path, "HumanPyramids.cpp") == 0
