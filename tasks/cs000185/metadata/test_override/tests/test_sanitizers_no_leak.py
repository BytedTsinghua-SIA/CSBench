import subprocess
from pathlib import Path


def test_sanitizers_no_leak():
    # Run gtest binary; ensure no errors/leaks with ASAN/LSAN enabled
    cwd = Path(__file__).resolve().parent.parent
    binary = cwd / "build/test/count_min_sketch_test"

    assert binary.exists(), f"Missing file: {binary}"

    cmd = f"bash -lc '{binary}'"
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        # 容器内 Debug 构建已启用 ASAN/LSAN；无需额外 env
    )

    output = result.stdout or ""

    # Exit code should be 0; ASAN/LSAN errors cause non-zero exit
    assert result.returncode == 0, (
        "Expected test binary to exit with code 0 under ASAN/LSAN.\n"
        f"Exit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
    )

    # Output should not contain sanitizer error markers
    bad_markers = [
        "ERROR: AddressSanitizer",
        "LeakSanitizer: detected memory leaks",
        "SUMMARY: AddressSanitizer",
        "SUMMARY: LeakSanitizer",
    ]
    assert not any(m in output for m in bad_markers), (
        "Sanitizer reported memory error/leak in output.\n"
        f"--- output ---\n{output}\n--------------\n"
    )
