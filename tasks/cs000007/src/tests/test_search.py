import subprocess
from pathlib import Path
import pytest

# The test script is in /<proj_root>/tests. The project root is one level up.
PROJ_ROOT = Path(__file__).resolve().parent.parent
SEARCH_EXEC = PROJ_ROOT / "search"
IMDBTEST_EXEC = PROJ_ROOT / "imdbtest"

def test_imdbtest():
    """
    Tests the imdb class implementation by running the imdbtest harness.
    """
    assert IMDBTEST_EXEC.exists(), f"Missing executable: {IMDBTEST_EXEC}"

    cmd = [str(IMDBTEST_EXEC), "Kevin Bacon (I)"]
    result = subprocess.run(
        cmd,
        cwd=str(PROJ_ROOT),
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, (
        f"imdbtest failed with exit code {result.returncode}\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}\n"
    )


def run_search_test(actors, expected_path_length, test_name):
    assert SEARCH_EXEC.exists(), f"Missing executable: {SEARCH_EXEC}"

    cmd = [str(SEARCH_EXEC)] + actors
    result = subprocess.run(
        cmd,
        cwd=str(PROJ_ROOT),  # Run from the project root so "./slink" can be found
        check=False,
        text=True,
        capture_output=True,
    )

    output = result.stdout or ""
    
    if expected_path_length > 0:
        path_lines = [line for line in output.splitlines() if "was in" in line]
        actual_path_length = len(path_lines)
        assert actual_path_length == expected_path_length, (
            f"Test '{test_name}' failed.\n"
            f"Expected path length {expected_path_length}, but found {actual_path_length}.\n"
            f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
        )
    else: # expected_path_length == 0, meaning no path
        assert "No path between those two people could be found." in output, (
            f"Test '{test_name}' failed.\n"
            f"Expected to find 'No path' message in the output.\n"
            f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
        )


@pytest.mark.parametrize("test_name, actors, expected_path_length", [
    (
        "Direct Connection (Length 1)",
        ["Meryl Streep", "Jack Nicholson (I)"],
        1
    ),
    (
        "Indirect Connection (Length 2)",
        ["Mary Tyler Moore", "Red Buttons"],
        2
    ),
    (
        "Longer Connection (Length 3)",
        ["Jerry Cain", "Kevin Bacon (I)"],
        3
    ),
    (
        "Longest Connection (Length 5)",
        ["Danzel Muzingo", "Liseli Mutti"],
        5
    ),
    (
        "No Path Found",
        ["Tom Hanks", "This Actor Does Not Exist"],
        0
    )
])
def test_shortest_path(test_name, actors, expected_path_length):
    run_search_test(actors, expected_path_length, test_name)


def test_invalid_arguments():
    """Tests the program's response to an incorrect number of arguments."""
    assert SEARCH_EXEC.exists(), f"Missing executable: {SEARCH_EXEC}"

    cmd = [str(SEARCH_EXEC), "Tom Hanks"]
    result = subprocess.run(
        cmd,
        cwd=str(PROJ_ROOT),
        check=False,
        text=True,
        capture_output=True,
    )

    output = result.stdout or ""
    assert "Usage:" in output, (
        "Test 'Invalid Arguments' failed.\n"
        "Expected to find a usage message in the output.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )