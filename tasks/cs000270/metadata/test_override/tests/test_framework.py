from pathlib import Path

def test_files_exist():
    cwd = Path(__file__).resolve().parent.parent

    problem1 = cwd / "problem1.py"
    problem2 = cwd / "problem2.py"

    assert problem1.exists(), f"Missing file: {problem1}"
    assert problem2.exists(), f"Missing file: {problem2}"
