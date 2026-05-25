"""
Pytest configuration and shared utilities
"""
import os
import subprocess
import tempfile
import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_build():
    """Ensure project is built before running tests"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_dir = os.path.join(base_dir, "build")
    
    if not os.path.exists(build_dir) or not os.path.exists(os.path.join(build_dir, "lib")):
        # Build the project
        os.makedirs(build_dir, exist_ok=True)
        subprocess.run(["cmake", ".."], cwd=build_dir, check=True)
        try:
            subprocess.run(["make", "-j"], cwd=build_dir, check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["make", "-j1"], cwd=build_dir, check=True)
    
    # Set library path
    lib_path = os.path.join(build_dir, "lib")
    util_path = os.path.join(build_dir, "util")
    current_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = f"{lib_path}:{util_path}:{current_ld_path}".rstrip(":")


@pytest.fixture(scope="session")
def build_dir():
    """Get the build directory path"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_dir = os.path.join(base_dir, "build")
    return build_dir


def compile_cpp_test(source_code, output_name, build_dir):
    """Compile a C++ test program"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cc', delete=False) as f:
        f.write(source_code)
        source_file = f.name
    
    try:
        # Include paths
        lib_dir = os.path.join(os.path.dirname(build_dir), "lib")
        util_dir = os.path.join(os.path.dirname(build_dir), "util")
        
        # Library paths
        lib_path = os.path.join(build_dir, "lib")
        util_path = os.path.join(build_dir, "util")
        
        cmd = [
            'g++', '-std=c++20',
            f'-I{lib_dir}', f'-I{util_dir}',
            source_file,
            f'-L{lib_path}', f'-L{util_path}',
            '-lminnow_debug', '-lutil_debug',
            '-o', output_name
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=build_dir
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Compilation failed: {result.stderr}")
        return True
    finally:
        if os.path.exists(source_file):
            os.unlink(source_file)

