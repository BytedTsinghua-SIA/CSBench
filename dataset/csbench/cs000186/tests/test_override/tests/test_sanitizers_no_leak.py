import subprocess
from pathlib import Path


def test_sanitizers_no_leak():
    # Run four gtest binaries sequentially; ensure no crash/leak under ASAN/LSAN-enabled Debug build
    cwd = Path(__file__).resolve().parent.parent

    binaries = [
        cwd / "build/test/arc_replacer_test",
        cwd / "build/test/disk_scheduler_test",
        cwd / "build/test/buffer_pool_manager_test",
        cwd / "build/test/page_guard_test",
    ]

    bad_markers = [
        "ERROR: AddressSanitizer",
        "LeakSanitizer: detected memory leaks",
        "SUMMARY: AddressSanitizer",
        "SUMMARY: LeakSanitizer",
    ]

    for binary in binaries:
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
            # ASAN/LSAN are enabled in Debug build; no extra env required
        )

        output = result.stdout or ""

        # Return code must be 0; sanitizer errors typically produce non-zero exit
        assert result.returncode == 0, (
            "Expected test binary to exit with code 0 under ASAN/LSAN.\n"
            f"Binary: {binary}\nExit code: {result.returncode}\n--- output ---\n{output}\n--------------\n"
        )

        # Output should not contain sanitizer error/leak markers
        assert not any(m in output for m in bad_markers), (
            "Sanitizer reported memory error/leak in output.\n"
            f"Binary: {binary}\n--- output ---\n{output}\n--------------\n"
        )
