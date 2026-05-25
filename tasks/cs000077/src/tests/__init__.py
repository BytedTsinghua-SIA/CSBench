"""Reference solution tests package marker with standalone fallback."""

import sys
from pathlib import Path


def _bootstrap_path():
    tests_dir = Path(__file__).resolve()
    src_root = tests_dir.parent.parent  # .../src_correct
    repo_conftest = src_root.parent / "conftest.py"
    if repo_conftest.exists():
        return
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))


_bootstrap_path()
