"""
Pytest configuration and fixtures for CS144 Lab Checkpoint 1 tests.
"""

import os
import subprocess
import pytest
from pathlib import Path

def pytest_configure(config):
    config.option.console_output_style = "count"
    
@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


@pytest.fixture(scope="session")
def build_dir(project_root):
    """Get or create the build directory."""
    build_path = project_root / "build"
    return build_path


@pytest.fixture(scope="session", autouse=True)
def setup_build_environment(project_root, build_dir):
    """Set up the build environment before running any tests."""
    try:
        # Configure CMake if not already configured
        if not (build_dir / "CMakeCache.txt").exists():
            result = subprocess.run(
                ["cmake", "-S", ".", "-B", "build"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                pytest.fail(f"CMake configuration failed: {result.stderr}")
        
        # Build the project (functionality_testing target)
        result = subprocess.run(
            ["cmake", "--build", "build", "--target", "functionality_testing"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode != 0:
            pytest.fail(f"Build failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        pytest.fail("Build timed out")
    except FileNotFoundError:
        pytest.fail("CMake not found")
    except Exception as e:
        pytest.fail(f"Build setup failed: {str(e)}")


def run_cpp_test(build_dir, test_name, timeout=30):
    """
    Run a C++ test executable and return the result.
    
    This function wraps test execution to ensure tests can only PASS or FAIL,
    never ERROR. Any exceptions are caught and converted to test failures.
    """
    try:
        # Try sanitized version first in tests subdirectory
        test_executable = build_dir / "tests" / f"{test_name}_sanitized"
        if not test_executable.exists():
            # Fall back to non-sanitized version in tests subdirectory
            test_executable = build_dir / "tests" / test_name
        
        if not test_executable.exists():
            # Try in build root (legacy location)
            test_executable = build_dir / f"{test_name}_sanitized"
            if not test_executable.exists():
                test_executable = build_dir / test_name
        
        if not test_executable.exists():
            return False, f"Test executable not found: {test_name}"
        
        result = subprocess.run(
            [str(test_executable)],
            cwd=build_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            return True, "Test passed"
        else:
            error_msg = result.stderr if result.stderr else result.stdout
            return False, f"Test failed with return code {result.returncode}: {error_msg}"
    
    except subprocess.TimeoutExpired:
        return False, f"Test {test_name} timed out after {timeout} seconds"
    except Exception as e:
        return False, f"Test execution failed: {str(e)}"


@pytest.fixture
def cpp_test_runner(build_dir):
    """Provide a test runner fixture for C++ tests."""
    def runner(test_name, timeout=30):
        return run_cpp_test(build_dir, test_name, timeout)
    return runner
