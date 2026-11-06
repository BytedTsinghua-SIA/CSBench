import importlib.util
import pathlib
import sys


def _load_grader():
    root = pathlib.Path(__file__).resolve().parents[1]
    grader_path = root / "wep" / "grader.py"
    module_dir = grader_path.parent
    sys.path.insert(0, str(module_dir))
    try:
        spec = importlib.util.spec_from_file_location("wep_grader_attack_two", grader_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def test_attack_two():
    grader = _load_grader()
    try:
        grader.grade_two()
    except Exception:
        assert False
