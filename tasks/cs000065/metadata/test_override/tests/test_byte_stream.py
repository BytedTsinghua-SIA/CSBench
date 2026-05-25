"""
Unit tests for ByteStream (Checkpoint 1 prerequisite)
"""
import subprocess
import tempfile
import os
import pytest
import sys

# Add tests directory to path to import conftest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from conftest import compile_cpp_test


def test_byte_stream_basic_write_read(build_dir):
    """Test basic write and read operations"""
    code = '''
#include "byte_stream.hh"
#include <cassert>
#include <iostream>

int main() {
    ByteStream bs(100);
    bs.writer().push("hello");
    assert(bs.reader().bytes_buffered() == 5);
    assert(bs.reader().peek() == "hello");
    bs.reader().pop(5);
    assert(bs.reader().bytes_buffered() == 0);
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False, dir=build_dir) as f:
        exe_name = f.name
    
    try:
        compile_cpp_test(code, exe_name, build_dir)
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{os.path.join(build_dir, 'lib')}:{os.path.join(build_dir, 'util')}:{env.get('LD_LIBRARY_PATH', '')}"
        result = subprocess.run([exe_name], capture_output=True, text=True, env=env)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)


def test_byte_stream_capacity_limit(build_dir):
    """Test that ByteStream respects capacity limits"""
    code = '''
#include "byte_stream.hh"
#include <cassert>
#include <string>

int main() {
    ByteStream bs(5);
    bs.writer().push("hello");
    assert(bs.writer().available_capacity() == 0);
    bs.writer().push("world");
    assert(bs.reader().bytes_buffered() == 5);
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False, dir=build_dir) as f:
        exe_name = f.name
    
    try:
        compile_cpp_test(code, exe_name, build_dir)
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{os.path.join(build_dir, 'lib')}:{os.path.join(build_dir, 'util')}:{env.get('LD_LIBRARY_PATH', '')}"
        result = subprocess.run([exe_name], capture_output=True, text=True, env=env)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)


def test_byte_stream_close(build_dir):
    """Test closing the stream"""
    code = '''
#include "byte_stream.hh"
#include <cassert>

int main() {
    ByteStream bs(100);
    bs.writer().push("test");
    bs.writer().close();
    assert(bs.writer().is_closed());
    assert(!bs.reader().is_finished());
    bs.reader().pop(4);
    assert(bs.reader().is_finished());
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False, dir=build_dir) as f:
        exe_name = f.name
    
    try:
        compile_cpp_test(code, exe_name, build_dir)
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{os.path.join(build_dir, 'lib')}:{os.path.join(build_dir, 'util')}:{env.get('LD_LIBRARY_PATH', '')}"
        result = subprocess.run([exe_name], capture_output=True, text=True, env=env)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)


def test_byte_stream_empty_stream(build_dir):
    """Test edge case: empty stream"""
    code = '''
#include "byte_stream.hh"
#include <cassert>

int main() {
    ByteStream bs(100);
    assert(bs.reader().bytes_buffered() == 0);
    assert(bs.reader().is_finished() == false);
    bs.writer().close();
    assert(bs.reader().is_finished() == true);
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False, dir=build_dir) as f:
        exe_name = f.name
    
    try:
        compile_cpp_test(code, exe_name, build_dir)
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = f"{os.path.join(build_dir, 'lib')}:{os.path.join(build_dir, 'util')}:{env.get('LD_LIBRARY_PATH', '')}"
        result = subprocess.run([exe_name], capture_output=True, text=True, env=env)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)

