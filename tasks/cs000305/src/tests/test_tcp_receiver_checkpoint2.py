from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

import pytest


_SRC_DIR = Path(__file__).resolve().parents[1]
_BUILD_DIR = _SRC_DIR / "build_pytest"


def _run(
    argv: List[str],
    *,
    cwd: Optional[Path] = None,
    timeout_s: int = 1800,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            argv,
            cwd=str(cwd) if cwd is not None else None,
            text=True,
            capture_output=True,
            timeout=timeout_s,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"command failed to run (pytest error avoided): {argv!r}\n{exc!r}")
        raise  # unreachable


def _ensure_cmake_configured() -> None:
    _BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # Configure step is idempotent; keep it simple and robust.
    # Prefer a single-config generator when available to avoid needing `ctest -C`.
    cmake_args = ["cmake", "-S", str(_SRC_DIR), "-B", str(_BUILD_DIR)]
    if os.name == "nt":
        # If Ninja is installed, it tends to work better cross-platform.
        ninja = shutil.which("ninja")
        if ninja is not None:
            cmake_args += ["-G", "Ninja"]

    proc = _run(cmake_args)
    if proc.returncode != 0:
        pytest.fail(
            "cmake configure failed\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}\n"
        )


def _ctest_run(regex: str) -> None:
    _ensure_cmake_configured()

    config_args: List[str] = []
    if os.name == "nt":
        # For VS multi-config generators, ctest needs a configuration.
        # If we ended up with a single-config generator, -C is harmless.
        config_args = ["-C", os.environ.get("CMAKE_BUILD_CONFIG", "Debug")]

    args = [
        "ctest",
        "--test-dir",
        str(_BUILD_DIR),
        *config_args,
        "--output-on-failure",
        "--stop-on-failure",
        "--timeout",
        "60",
        "-R",
        regex,
    ]
    proc = _run(args)
    if proc.returncode != 0:
        pytest.fail(
            f"ctest failed (pattern={regex!r})\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}\n"
        )


@pytest.fixture(scope="session", autouse=True)
def _sanity_check_repo_layout() -> None:
    if not (_SRC_DIR / "CMakeLists.txt").exists():
        pytest.fail(f"expected CMake project under: {_SRC_DIR}")


# --- Checkpoint 2: TCP Receiver ---
# These pytest tests wrap the existing C++ test harnesses (recv_*), each of which
# exercises a specific functional requirement described in metadata/task.md.


def test_tcp_receiver_handles_syn_and_ackno_generation() -> None:
    """SYN establishes ISN; receiver generates correct ackno progression."""
    _ctest_run(r"^recv_connect$")


def test_tcp_receiver_reassembles_payload_and_advances_ackno() -> None:
    """Payload bytes are reassembled into the ByteStream and ack advances."""
    _ctest_run(r"^recv_transmit$")


def test_tcp_receiver_window_size_tracks_available_capacity() -> None:
    """Window size reflects remaining ByteStream capacity (capped to uint16)."""
    _ctest_run(r"^recv_window$")


def test_tcp_receiver_handles_out_of_order_and_overlaps() -> None:
    """Sequence-number translation + reassembly works for reordering/overlap."""
    _ctest_run(r"^recv_reorder$|^recv_reorder_more$")


def test_tcp_receiver_handles_fin_rst_and_special_cases() -> None:
    """FIN consumes seqno, RST propagates stream error; edge cases handled."""
    _ctest_run(r"^recv_special$|^recv_close$")
