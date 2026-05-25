"""
Unit tests for Router (Checkpoint 6)
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


def test_router_add_route():
    """Test adding routes to routing table"""
    code = '''
#include "router.hh"
#include "network_interface.hh"
#include "address.hh"
#include <cassert>
#include <memory>

class TestOutput : public NetworkInterface::OutputPort {
public:
    void transmit(const NetworkInterface&, const EthernetFrame&) override {}
};

int main() {
    Router router;
    auto iface = std::make_shared<NetworkInterface>(
        "eth0", std::make_shared<TestOutput>(),
        EthernetAddress{0x02, 0, 0, 0, 0, 1},
        Address("10.0.0.1")
    );
    size_t id = router.add_interface(iface);
    router.add_route(Address("10.0.0.0").ipv4_numeric(), 24, {}, id);
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


def test_router_forward_packet():
    """Test forwarding IP packets"""
    code = '''
#include "router.hh"
#include "network_interface.hh"
#include "address.hh"
#include "ipv4_datagram.hh"
#include <cassert>
#include <memory>

class TestOutput : public NetworkInterface::OutputPort {
public:
    void transmit(const NetworkInterface&, const EthernetFrame&) override {}
};

int main() {
    Router router;
    auto iface1 = std::make_shared<NetworkInterface>(
        "eth0", std::make_shared<TestOutput>(),
        EthernetAddress{0x02, 0, 0, 0, 0, 1},
        Address("10.0.0.1")
    );
    auto iface2 = std::make_shared<NetworkInterface>(
        "eth1", std::make_shared<TestOutput>(),
        EthernetAddress{0x02, 0, 0, 0, 0, 2},
        Address("192.168.1.1")
    );
    
    size_t id1 = router.add_interface(iface1);
    size_t id2 = router.add_interface(iface2);
    router.add_route(Address("10.0.0.0").ipv4_numeric(), 24, {}, id1);
    router.add_route(Address("192.168.1.0").ipv4_numeric(), 24, {}, id2);
    
    InternetDatagram dgram;
    dgram.header.src = Address("10.0.0.2").ipv4_numeric();
    dgram.header.dst = Address("192.168.1.2").ipv4_numeric();
    dgram.header.ttl = 64;
    dgram.header.compute_checksum();
    
    iface1->send_datagram(dgram, Address("192.168.1.2"));
    router.route();
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


def test_router_ttl_decrement():
    """Test TTL decrement on forwarding"""
    code = '''
#include "router.hh"
#include "network_interface.hh"
#include "address.hh"
#include <cassert>
#include <memory>

class TestOutput : public NetworkInterface::OutputPort {
public:
    void transmit(const NetworkInterface&, const EthernetFrame&) override {}
};

int main() {
    Router router;
    auto iface = std::make_shared<NetworkInterface>(
        "eth0", std::make_shared<TestOutput>(),
        EthernetAddress{0x02, 0, 0, 0, 0, 1},
        Address("10.0.0.1")
    );
    size_t id = router.add_interface(iface);
    router.add_route(Address("0.0.0.0").ipv4_numeric(), 0, Address("10.0.0.2"), id);
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


def test_router_destination_unreachable():
    """Test handling destination unreachable (ICMP error)"""
    code = '''
#include "router.hh"
#include "network_interface.hh"
#include "address.hh"
#include "ipv4_datagram.hh"
#include <cassert>
#include <memory>

class TestOutput : public NetworkInterface::OutputPort {
public:
    void transmit(const NetworkInterface&, const EthernetFrame&) override {}
};

int main() {
    Router router;
    auto iface = std::make_shared<NetworkInterface>(
        "eth0", std::make_shared<TestOutput>(),
        EthernetAddress{0x02, 0, 0, 0, 0, 1},
        Address("10.0.0.1")
    );
    size_t id = router.add_interface(iface);
    router.add_route(Address("10.0.0.0").ipv4_numeric(), 24, {}, id);
    
    InternetDatagram dgram;
    dgram.header.src = Address("10.0.0.2").ipv4_numeric();
    dgram.header.dst = Address("192.168.1.2").ipv4_numeric();
    dgram.header.ttl = 64;
    dgram.header.compute_checksum();
    
    iface->send_datagram(dgram, Address("192.168.1.2"));
    router.route();
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


def test_router_ttl_expired():
    """Test handling TTL expired packets"""
    code = '''
#include "router.hh"
#include "network_interface.hh"
#include "address.hh"
#include "ipv4_datagram.hh"
#include <cassert>
#include <memory>

class TestOutput : public NetworkInterface::OutputPort {
public:
    void transmit(const NetworkInterface&, const EthernetFrame&) override {}
};

int main() {
    Router router;
    auto iface = std::make_shared<NetworkInterface>(
        "eth0", std::make_shared<TestOutput>(),
        EthernetAddress{0x02, 0, 0, 0, 0, 1},
        Address("10.0.0.1")
    );
    size_t id = router.add_interface(iface);
    router.add_route(Address("0.0.0.0").ipv4_numeric(), 0, Address("10.0.0.2"), id);
    
    InternetDatagram dgram;
    dgram.header.src = Address("10.0.0.2").ipv4_numeric();
    dgram.header.dst = Address("192.168.1.2").ipv4_numeric();
    dgram.header.ttl = 1;
    dgram.header.compute_checksum();
    
    iface->send_datagram(dgram, Address("192.168.1.2"));
    router.route();
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

