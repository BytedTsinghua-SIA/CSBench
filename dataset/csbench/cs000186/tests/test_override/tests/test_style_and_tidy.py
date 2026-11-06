import subprocess
from pathlib import Path


def _run(cmd: str, cwd: Path):
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout or ""


def test_make_format_and_clang_tidy():
    # Run make targets in the build directory
    project_root = Path(__file__).resolve().parent.parent
    build_dir = project_root / "build"

    # 1) Automatic formatting (should succeed)
    rc1, out1 = _run("bash -lc 'make format'", build_dir)
    assert rc1 == 0, (
        "Expected 'make format' to succeed.\n"
        f"Exit code: {rc1}\n--- output ---\n{out1}\n--------------\n"
    )

    # 2) Basic clang-tidy check (p0 target covers primer-related code)
    rc2, out2 = _run("bash -lc 'make check-clang-tidy-p1'", build_dir)
    assert rc2 == 0, (
        "Expected 'make check-clang-tidy-p1' to succeed.\n"
        f"Exit code: {rc2}\n--- output ---\n{out2}\n--------------\n"
    )
