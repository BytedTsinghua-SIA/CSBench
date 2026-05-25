from _simpletest_helper import run_group


def test_disasterplanning(tmp_path):
    assert run_group(tmp_path, "DisasterPlanning.cpp") == 0
