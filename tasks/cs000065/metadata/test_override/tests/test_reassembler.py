"""
Unit tests for Reassembler (Checkpoint 1)
"""
import subprocess
import tempfile
import os
import pytest
import sys

# Add tests directory to path to import conftest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from conftest import compile_cpp_test


def compile_test_program(source_code, output_name):
    """Compile a C++ test program"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_dir = os.path.join(base_dir, "build")
    return compile_cpp_test(source_code, output_name, build_dir)


def test_reassembler_ordered_insert():
    """Test inserting segments in order"""
    code = '''
#include "reassembler.hh"
#include <cassert>
#include <string>

int main() {
    Reassembler r(ByteStream(1000));
    r.insert(0, "abc", false);
    r.insert(3, "def", true);
    assert(r.reader().bytes_popped() == 0);
    assert(r.reader().bytes_buffered() == 6);
    std::string result;
    read(r.reader(), 100, result);
    assert(result == "abcdef");
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False) as f:
        exe_name = f.name
    
    try:
        compile_test_program(code, exe_name)
        result = subprocess.run([exe_name], capture_output=True, text=True)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)


def test_reassembler_out_of_order():
    """Test handling out-of-order segments"""
    code = '''
#include "reassembler.hh"
#include <cassert>
#include <string>

int main() {
    Reassembler r(ByteStream(1000));
    r.insert(3, "def", false);
    assert(r.count_bytes_pending() > 0);
    r.insert(0, "abc", true);
    std::string result;
    read(r.reader(), 100, result);
    assert(result == "abcdef");
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False) as f:
        exe_name = f.name
    
    try:
        compile_test_program(code, exe_name)
        result = subprocess.run([exe_name], capture_output=True, text=True)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)


def test_reassembler_duplicate_data():
    """Test handling duplicate data"""
    code = '''
#include "reassembler.hh"
#include <cassert>
#include <string>

int main() {
    Reassembler r(ByteStream(1000));
    r.insert(0, "abc", false);
    r.insert(0, "abc", false);
    r.insert(3, "def", true);
    std::string result;
    read(r.reader(), 100, result);
    assert(result == "abcdef");
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False) as f:
        exe_name = f.name
    
    try:
        compile_test_program(code, exe_name)
        result = subprocess.run([exe_name], capture_output=True, text=True)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)


def test_reassembler_capacity_limit():
    """Test that reassembler respects capacity limits"""
    code = '''
#include "reassembler.hh"
#include <cassert>

int main() {
    Reassembler r(ByteStream(5));
    r.insert(0, "hello", false);
    r.insert(5, "world", true);
    assert(r.reader().bytes_buffered() <= 5);
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False) as f:
        exe_name = f.name
    
    try:
        compile_test_program(code, exe_name)
        result = subprocess.run([exe_name], capture_output=True, text=True)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)


def test_reassembler_exceeds_window():
    """Test handling fragments that exceed the window"""
    code = '''
#include "reassembler.hh"
#include <cassert>
#include <string>

int main() {
    Reassembler r(ByteStream(5));
    r.insert(0, "abc", false);
    r.insert(3, "defghij", false);
    assert(r.reader().bytes_buffered() <= 5);
    std::string result;
    read(r.reader(), 100, result);
    assert(result.length() <= 5);
    return 0;
}
'''
    with tempfile.NamedTemporaryFile(delete=False) as f:
        exe_name = f.name
    
    try:
        compile_test_program(code, exe_name)
        result = subprocess.run([exe_name], capture_output=True, text=True)
        assert result.returncode == 0, f"Test failed: {result.stderr}"
    finally:
        if os.path.exists(exe_name):
            os.unlink(exe_name)

