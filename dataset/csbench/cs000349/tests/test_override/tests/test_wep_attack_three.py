import importlib.util
import pathlib
import sys


def _load_grader():
    root = pathlib.Path(__file__).resolve().parents[1]
    grader_path = root / "wep" / "grader.py"
    module_dir = grader_path.parent
    sys.path.insert(0, str(module_dir))
    try:
        spec = importlib.util.spec_from_file_location("wep_grader_attack_three", grader_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def test_attack_three():
    grader = _load_grader()
    try:
        grader.grade_three()
    except Exception:
        assert False
