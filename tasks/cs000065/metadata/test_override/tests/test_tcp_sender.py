"""
Unit tests for TCPSender (Checkpoint 3)
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


def test_tcp_sender_syn():
    """Test sending SYN segment"""
    code = '''
#include "tcp_sender.hh"
#include "wrapping_integers.hh"
#include <cassert>
#include <queue>

int main() {
    TCPSender sender(ByteStream(1000), Wrap32(0), 100);
    std::queue<TCPSenderMessage> output;
    sender.push([&](const TCPSenderMessage& msg) { output.push(msg); });
    assert(!output.empty());
    auto msg = output.front();
    assert(msg.SYN);
    assert(msg.seqno == Wrap32(0));
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


def test_tcp_sender_sliding_window():
    """Test sliding window protocol"""
    code = '''
#include "tcp_sender.hh"
#include "tcp_receiver_message.hh"
#include "wrapping_integers.hh"
#include <cassert>
#include <queue>

int main() {
    TCPSender sender(ByteStream(1000), Wrap32(0), 100);
    std::queue<TCPSenderMessage> output;
    
    sender.push([&](const TCPSenderMessage& msg) { output.push(msg); });
    TCPReceiverMessage ack;
    ack.ackno = Wrap32(1);
    ack.window_size = 10;
    sender.receive(ack);
    
    sender.writer().push("hello");
    sender.push([&](const TCPSenderMessage& msg) { output.push(msg); });
    assert(output.size() >= 2);
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


def test_tcp_sender_retransmission():
    """Test timeout retransmission"""
    code = '''
#include "tcp_sender.hh"
#include "wrapping_integers.hh"
#include <cassert>
#include <queue>

int main() {
    TCPSender sender(ByteStream(1000), Wrap32(0), 100);
    std::queue<TCPSenderMessage> output;
    
    sender.push([&](const TCPSenderMessage& msg) { output.push(msg); });
    size_t initial_size = output.size();
    
    sender.tick(150, [&](const TCPSenderMessage& msg) { output.push(msg); });
    assert(output.size() > initial_size);
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


def test_tcp_sender_sequence_numbers():
    """Test sequence number tracking"""
    code = '''
#include "tcp_sender.hh"
#include "wrapping_integers.hh"
#include <cassert>

int main() {
    TCPSender sender(ByteStream(1000), Wrap32(0), 100);
    assert(sender.sequence_numbers_in_flight() == 0);
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


def test_tcp_sender_congestion_control():
    """Test basic congestion control mechanism"""
    code = '''
#include "tcp_sender.hh"
#include "tcp_receiver_message.hh"
#include "wrapping_integers.hh"
#include <cassert>
#include <queue>

int main() {
    TCPSender sender(ByteStream(1000), Wrap32(0), 100);
    std::queue<TCPSenderMessage> output;
    
    sender.push([&](const TCPSenderMessage& msg) { output.push(msg); });
    TCPReceiverMessage ack;
    ack.ackno = Wrap32(1);
    ack.window_size = 5;
    sender.receive(ack);
    
    sender.writer().push("hello world");
    sender.push([&](const TCPSenderMessage& msg) { output.push(msg); });
    
    assert(sender.sequence_numbers_in_flight() <= 5);
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


def test_tcp_sender_fin():
    """Test sending FIN segment"""
    code = '''
#include "tcp_sender.hh"
#include "tcp_receiver_message.hh"
#include "wrapping_integers.hh"
#include <cassert>
#include <queue>

int main() {
    TCPSender sender(ByteStream(1000), Wrap32(0), 100);
    std::queue<TCPSenderMessage> output;
    
    sender.push([&](const TCPSenderMessage& msg) { output.push(msg); });
    TCPReceiverMessage ack;
    ack.ackno = Wrap32(1);
    ack.window_size = 10;
    sender.receive(ack);
    
    sender.writer().close();
    sender.push([&](const TCPSenderMessage& msg) { output.push(msg); });
    
    bool has_fin = false;
    while (!output.empty()) {
        if (output.front().FIN) {
            has_fin = true;
            break;
        }
        output.pop();
    }
    assert(has_fin);
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

