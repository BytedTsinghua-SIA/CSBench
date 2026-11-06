from _simpletest_helper import run_group


def test_whatareyoudoing(tmp_path):
    assert run_group(tmp_path, "WhatAreYouDoing.cpp") == 0
