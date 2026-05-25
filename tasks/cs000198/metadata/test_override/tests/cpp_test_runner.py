#!/usr/bin/env python3
"""
Helper module: Compile and run C++ tests, then parse results
"""

import subprocess
import os
import sys
import tempfile
import shutil
from pathlib import Path


class CppTestRunner:
    """Helper class to compile and run C++ tests"""
    
    def __init__(self, test_name, cpp_test_file):
        """
        Initialize test runner
        
        Args:
            test_name: Test name (e.g., 'fdp', 'ghb', 'task3')
            cpp_test_file: C++ test file path (relative to ctest directory)
        """
        self.test_name = test_name
        self.cpp_test_file = cpp_test_file
        
        # Get project root directory
        # In Docker container, the build context is src/, so files are copied to /testbed
        # In local environment, we need to go up from tests/ to src/ to project root
        current_file = Path(__file__).resolve()
        
        # Check if we're in Docker container (/testbed) or local environment
        # In Docker: current_file is /testbed/tests/cpp_test_runner.py
        #   current_file.parent.parent = /testbed
        # In local: current_file is .../CS000198/src/tests/cpp_test_runner.py
        #   current_file.parent.parent = .../CS000198/src
        tests_dir = current_file.parent  # tests/
        parent_dir = tests_dir.parent.resolve()    # src/ or /testbed
        
        # Check if we're in Docker by comparing with /testbed
        testbed_path = Path('/testbed').resolve()
        if parent_dir == testbed_path:
            # Docker environment: /testbed is the root (which contains src/ contents)
            self.project_root = parent_dir
            self.src_dir = self.project_root
            self.ctest_dir = self.src_dir / "ctest"
            self.inc_dir = self.src_dir / "inc"
            self.prefetcher_dir = self.src_dir / "prefetcher"
        else:
            # Local environment: go up from tests/ to src/ to project root
            # current_file is in src/tests/, so:
            # parent = src/tests/
            # parent.parent = src/
            # parent.parent.parent = project root (CS000198/)
            self.project_root = parent_dir.parent
            self.src_dir = parent_dir
            self.ctest_dir = self.src_dir / "ctest"
            self.inc_dir = self.src_dir / "inc"
            self.prefetcher_dir = self.src_dir / "prefetcher"
        
        # Temporary directory for compilation
        self.temp_dir = None
        self.executable = None
    
    def __enter__(self):
        """Context manager entry"""
        self.temp_dir = tempfile.mkdtemp(prefix=f"test_{self.test_name}_")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit, cleanup temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def compile_test(self):
        """Compile C++ test file"""
        cpp_file = self.ctest_dir / self.cpp_test_file
        cpp_file = cpp_file.resolve()  # Ensure absolute path
        
        if not cpp_file.exists():
            # Provide more detailed error information
            error_msg = (
                f"C++ test file does not exist: {cpp_file}\n"
                f"  Looking in: {self.ctest_dir}\n"
                f"  Test file name: {self.cpp_test_file}\n"
                f"  CTest directory exists: {self.ctest_dir.exists()}\n"
            )
            if self.ctest_dir.exists():
                available_files = list(self.ctest_dir.glob("*.cpp"))
                error_msg += f"  Available .cpp files: {[f.name for f in available_files]}\n"
            raise FileNotFoundError(error_msg)
        
        # Compilation command
        cxx = os.environ.get('CXX', 'g++')
        executable = os.path.join(self.temp_dir, f"test_{self.test_name}")
        
        cxxflags = [
            '-Wall', '-O0', '-std=c++11', '-g',  # Use -O0 to prevent optimization of static initializers
            f'-I{self.inc_dir}',
            f'-I{self.src_dir}',
            f'-I{self.prefetcher_dir}',
            '-DNUM_CPUS=1'
        ]
        
        # Source files to link
        # Note: We link cache_stub.cc which provides minimal implementations
        # of CACHE virtual functions needed for testing
        sources = [
            str(cpp_file),
            str(self.ctest_dir / "test_main.cpp"),
            str(self.ctest_dir / "cache_stub.cc"),
        ]
        
        cmd = [cxx] + cxxflags + sources + ['-o', executable]
        
        try:
            # Run compilation from ctest directory to resolve relative paths in #include statements
            result = subprocess.run(
                cmd,
                cwd=str(self.ctest_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                error_msg = f"Compilation failed:\n{result.stderr}\nCommand: {' '.join(cmd)}"
                raise RuntimeError(error_msg)
            
            self.executable = executable
            return True
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Compilation timeout")
        except Exception as e:
            raise RuntimeError(f"Compilation error: {str(e)}")
    
    def run_test(self, test_name=None):
        """
        Run compiled test and return results
        
        Args:
            test_name: If provided, run only this specific test. Otherwise run all tests.
        """
        if not self.executable or not os.path.exists(self.executable):
            raise RuntimeError("Test executable does not exist, please compile first")
        
        try:
            cmd = [self.executable]
            if test_name:
                cmd.append(test_name)
            
            result = subprocess.run(
                cmd,
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Test execution timeout',
                'success': False
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'success': False
            }
    
    def parse_test_results(self, output):
        """Parse test output and extract test results"""
        lines = output.split('\n')
        results = {
            'passed': [],
            'failed': [],
            'total_passed': 0,
            'total_failed': 0
        }
        
        current_test = None
        for line in lines:
            if 'Running test:' in line:
                # Extract test name
                test_name = line.split('Running test:')[1].split('...')[0].strip()
                current_test = test_name
            elif 'PASSED' in line and current_test:
                results['passed'].append(current_test)
                results['total_passed'] += 1
                current_test = None
            elif 'FAILED' in line and current_test:
                results['failed'].append(current_test)
                results['total_failed'] += 1
                current_test = None
            elif 'Tests passed:' in line:
                # Try to extract number from summary
                try:
                    num = int(line.split('Tests passed:')[1].strip())
                    results['total_passed'] = num
                except:
                    pass
            elif 'Tests failed:' in line:
                try:
                    num = int(line.split('Tests failed:')[1].strip())
                    results['total_failed'] = num
                except:
                    pass
        
        return results


def run_cpp_test(test_name, cpp_test_file, specific_test=None):
    """
    Convenience function: Compile and run C++ test
    
    Args:
        test_name: Name of the test suite (e.g., 'fdp', 'ghb', 'task3')
        cpp_test_file: C++ test file path
        specific_test: If provided, run only this specific test. Otherwise run all tests.
    
    Returns:
        tuple: (success: bool, results: dict, output: str)
    """
    with CppTestRunner(test_name, cpp_test_file) as runner:
        try:
            runner.compile_test()
            result = runner.run_test(specific_test)
            
            if specific_test:
                # For single test, parse differently
                parsed = {
                    'passed': [],
                    'failed': [],
                    'total_passed': 1 if result['success'] else 0,
                    'total_failed': 0 if result['success'] else 1
                }
                if result['success']:
                    parsed['passed'].append(specific_test)
                else:
                    parsed['failed'].append(specific_test)
            else:
                parsed = runner.parse_test_results(result['stdout'])
            
            return (
                result['success'] and parsed['total_failed'] == 0,
                parsed,
                result['stdout'] + result['stderr']
            )
        except Exception as e:
            return (
                False,
                {'error': str(e)},
                str(e)
            )

