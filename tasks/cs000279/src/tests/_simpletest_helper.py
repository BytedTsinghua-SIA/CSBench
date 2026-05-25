from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT
GUI_DIR = SRC_DIR / "GUI"
RUNNER_CPP = ROOT / "tests" / "simpletest_runner.cpp"
DATAPOINT_ALLOC_CPP = SRC_DIR / "Demos" / "DataPointAlloc.cpp"


def _compiler():
    for candidate in ("g++", "clang++"):
        path = shutil.which(candidate)
        if path:
            return path
    return None


def build_runner(tmp_path):
    compiler = _compiler()
    if compiler is None:
        return None

    binary = tmp_path / "simpletest_runner"
    sources = [
        str(RUNNER_CPP),
        str(SRC_DIR / "Apportionment.cpp"),
        str(SRC_DIR / "HeapPQueue.cpp"),
        str(DATAPOINT_ALLOC_CPP),
        str(SRC_DIR / "GUI" / "SimpleTest.cpp"),
        str(SRC_DIR / "GUI" / "TestDriver.cpp"),
        str(SRC_DIR / "GUI" / "MemoryDiagnostics.cpp"),
        str(SRC_DIR / "GUI" / "TextUtils.cpp"),
    ]

    cmd = [
        compiler,
        "-std=c++17",
        "-O2",
        "-I",
        str(SRC_DIR),
        "-I",
        str(GUI_DIR),
        "-o",
        str(binary),
        *sources,
    ]

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        return None

    return binary


def run_group(tmp_path, group_name):
    binary = build_runner(tmp_path)
    if binary is None:
        return 1

    result = subprocess.run(
        [str(binary), "--group", group_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode
