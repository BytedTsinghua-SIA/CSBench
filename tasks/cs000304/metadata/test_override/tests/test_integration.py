"""
Pytest integration tests for Lab Checkpoint 1.

These tests verify the overall functionality of the checkpoint by
running the full check1 target which combines ByteStream and Reassembler tests.

Note: Tests can only PASS or FAIL, never ERROR.
"""

import pytest
import subprocess
from pathlib import Path


class TestCheckpointIntegration:
    """Integration tests for the entire Lab Checkpoint 1."""
    
    def test_check1_integration(self, project_root, build_dir):
        """
        Run the full check1 target to verify all Checkpoint 1 functionality.
        
        This test runs cmake --build build --target check1, which includes:
        - All ByteStream tests
        - All Reassembler tests
        - no_skip verification
        
        This is the ultimate verification that the checkpoint is complete.
        """
        try:
            # Run the check1 target
            result = subprocess.run(
                ["cmake", "--build", "build", "--target", "check1"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                assert True, "Checkpoint 1 integration test passed"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                assert False, f"Checkpoint 1 check failed: {error_msg}"
        
        except subprocess.TimeoutExpired:
            assert False, "Checkpoint 1 integration test timed out"
        except FileNotFoundError:
            assert False, "CMake not found - cannot run integration test"
        except Exception as e:
            assert False, f"Integration test failed with error: {str(e)}"


class TestBuildSystem:
    """Test the project build system."""
    
    def test_cmake_configuration(self, project_root):
        """
        Verify CMake configuration completes successfully.
        
        This test ensures the project can be configured with CMake,
        which is a prerequisite for building and testing.
        """
        try:
            build_dir = project_root / "build"
            
            result = subprocess.run(
                ["cmake", "-S", ".", "-B", "build"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                assert True, "CMake configuration succeeded"
            else:
                assert False, f"CMake configuration failed: {result.stderr}"
        
        except subprocess.TimeoutExpired:
            assert False, "CMake configuration timed out"
        except FileNotFoundError:
            assert False, "CMake not found"
        except Exception as e:
            assert False, f"CMake configuration error: {str(e)}"
    
    def test_project_compilation(self, project_root, build_dir):
        """
        Verify the project compiles successfully.
        
        This test ensures all source files compile without errors
        using the configured build system.
        """
        try:
            result = subprocess.run(
                ["cmake", "--build", "build"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                assert True, "Project compilation succeeded"
            else:
                # Check if it's a compilation error vs other issue
                if "error:" in result.stderr or "error:" in result.stdout:
                    assert False, f"Compilation error: {result.stderr or result.stdout}"
                else:
                    assert False, f"Build failed: {result.stderr or result.stdout}"
        
        except subprocess.TimeoutExpired:
            assert False, "Project compilation timed out"
        except FileNotFoundError:
            assert False, "CMake not found"
        except Exception as e:
            assert False, f"Compilation error: {str(e)}"
