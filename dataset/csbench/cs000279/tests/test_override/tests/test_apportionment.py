from _simpletest_helper import run_group


def test_apportionment(tmp_path):
    assert run_group(tmp_path, "Apportionment.cpp") == 0
