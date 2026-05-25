# tests/conftest.py
import types
import pytest
import gradelib
from gradelib import Runner

if not hasattr(gradelib, "options") or gradelib.options is None:
    gradelib.options = types.SimpleNamespace(
        verbose=False, color="auto", gdb=False, port=None,
        qemu_args="", make_flags="", timeout=None, qemu=None
    )

@pytest.fixture(scope="module")
def r():
    return Runner()