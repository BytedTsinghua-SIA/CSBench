import subprocess
from pathlib import Path


def test_java_tests_run():
    cwd = Path(__file__).resolve().parent.parent

    pom = cwd / "pom.xml"
    src_test_java = cwd / "src" / "test" / "java"

    assert pom.exists(), f"Missing file: {pom}"
    assert src_test_java.exists(), f"Missing directory: {src_test_java}"

    cmd = "bash -lc 'mvn -q test'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output = result.stdout or ""
    assert result.returncode == 0, (
        "Expected Maven tests to succeed.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

