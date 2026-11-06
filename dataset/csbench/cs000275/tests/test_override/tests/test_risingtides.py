from _simpletest_helper import run_group


def test_risingtides(tmp_path):
    assert run_group(tmp_path, "RisingTides.cpp") == 0
