import importlib.util
import pathlib
import sys


def _load_grader():
    root = pathlib.Path(__file__).resolve().parents[1]
    grader_path = root / "ecdsa" / "grader.py"
    module_dir = grader_path.parent
    sys.path.insert(0, str(module_dir))
    try:
        spec = importlib.util.spec_from_file_location("ecdsa_grader_problem1a", grader_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def test_problem_1a():
    grader = _load_grader()
    try:
        grader.test_1()
    except Exception:
        assert False
