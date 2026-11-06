from _simpletest_helper import run_group


def test_rosettastone(tmp_path):
    assert run_group(tmp_path, "RosettaStone.cpp") == 0
