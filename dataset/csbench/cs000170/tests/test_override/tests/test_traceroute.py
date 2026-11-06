import struct
import sys
from types import SimpleNamespace
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import traceroute  # noqa: E402


def test_ipv4_parses_basic_header():
    ver_ihl = (4 << 4) | 5
    tos = 0x1C
    total_len = 60
    ident = 0x1234
    flags = 0b010
    frag_offset = 0
    ttl = 64
    proto = 1
    checksum = 0xABCD
    src = 0x0A000001
    dst = 0x08080808

    header = struct.pack(
        "!BBHHHBBHII",
        ver_ihl,
        tos,
        total_len,
        ident,
        (flags << 13) | frag_offset,
        ttl,
        proto,
        checksum,
        src,
        dst,
    )

    ipv4 = traceroute.IPv4(header)

    assert ipv4.version == 4
    assert ipv4.header_len == 5
    assert ipv4.tos == tos
    assert ipv4.length == total_len
    assert ipv4.id == ident
    assert ipv4.flags == flags
    assert ipv4.frag_offset == frag_offset
    assert ipv4.ttl == ttl
    assert ipv4.proto == proto
    assert ipv4.cksum == checksum
    assert ipv4.src == src
    assert ipv4.dst == dst


def test_icmp_and_udp_parsers_decode_fields():
    icmp = traceroute.ICMP(bytes([11, 0, 0x1A, 0x2B]))
    assert traceroute.check_ttl_expired(icmp)
    assert icmp.code == 0
    assert icmp.cksum == 0x1A2B

    udp_bytes = struct.pack(
        "!HHHH", 54321, traceroute.TRACEROUTE_PORT_NUMBER, 32, 0xBEEF
    )
    udp = traceroute.UDP(udp_bytes)
    assert udp.src_port == 54321
    assert udp.dst_port == traceroute.TRACEROUTE_PORT_NUMBER
    assert udp.len == 32
    assert udp.cksum == 0xBEEF


def test_traceroute_discovers_unique_hops(monkeypatch):
    responses = {
        1: ["1.1.1.1", None, "1.1.1.1"],
        2: [None, "2.2.2.2", None],
    }

    def fake_recv_probe_response(sock, ttl):
        queue = responses.get(ttl)
        if not queue:
            return None
        return queue.pop(0)

    monkeypatch.setattr(traceroute, "recv_probe_response", fake_recv_probe_response)
    monkeypatch.setattr(traceroute.util, "print_result", lambda routers, ttl: None)

    class DummySend:
        def __init__(self):
            self.ttls = []
            self.sent_payloads = []

        def set_ttl(self, ttl):
            self.ttls.append(ttl)

        def sendto(self, payload, address):
            self.sent_payloads.append((payload, address))

    dummy_send = DummySend()
    route = traceroute.traceroute(dummy_send, SimpleNamespace(), "2.2.2.2")

    assert route == [["1.1.1.1"], ["2.2.2.2"]]
    assert dummy_send.ttls[:2] == [1, 2]
    for payload, address in dummy_send.sent_payloads:
        assert isinstance(payload, bytes)
        assert address[1] == traceroute.TRACEROUTE_PORT_NUMBER
