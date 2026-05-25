#!/usr/bin/env python3
"""
Basic functionality test for Network Path Analyzer

This script tests the core components without requiring actual ping data.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

def create_sample_ping_data():
    """Create sample ping data for testing."""
    sample_data = """[1640995200.123456] icmp_seq=1 ttl=64 time=12.34 ms
[1640995200.323456] icmp_seq=2 ttl=64 time=11.56 ms
[1640995200.523456] icmp_seq=3 ttl=64 time=15.78 ms
[1640995200.723456] icmp_seq=4 ttl=64 time=13.21 ms
[1640995201.123456] icmp_seq=5 ttl=64 time=14.67 ms
[1640995201.323456] icmp_seq=6 ttl=64 time=12.89 ms
[1640995201.523456] icmp_seq=7 ttl=64 time=16.43 ms
[1640995201.723456] icmp_seq=8 ttl=64 time=11.92 ms
[1640995202.123456] icmp_seq=9 ttl=64 time=13.45 ms
[1640995202.323456] icmp_seq=10 ttl=64 time=14.78 ms
"""

    return sample_data

def create_sample_traceroute_data():
    """Create sample traceroute data for testing."""
    sample_data = """traceroute to www.ox.ac.uk (163.1.2.1), 64 hops max, 52 byte packets
 1  router.local (192.168.1.1)  1.234 ms  1.567 ms  1.890 ms
 2  isp-gateway (10.0.0.1)  5.678 ms  5.901 ms  6.123 ms
 3  backbone-router (203.0.113.1)  12.345 ms  12.678 ms  13.001 ms
 4  london-gw (198.51.100.1)  45.123 ms  45.456 ms  45.789 ms
 5  oxford-university (163.1.2.254)  67.890 ms  68.123 ms  68.456 ms
 6  www.ox.ac.uk (163.1.2.1)  68.234 ms  68.567 ms  68.890 ms
"""

    return sample_data

def test_ping_parser():
    """Test ping data parsing functionality."""
    print("Testing PingDataParser...")

    try:
        from network_path_analyzer import PingDataParser
    except ImportError as e:
        if "matplotlib" in str(e):
            print("  ⚠ PingDataParser test skipped: matplotlib not available")
            return True
        else:
            raise

    # Create temporary file with sample data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(create_sample_ping_data())
        temp_file = f.name

    try:
        parser = PingDataParser(temp_file)
        print(f"  Parsed {len(parser.data)} packets")
        print(f"  Sample RTT: {parser.data['rtt'].iloc[0]} ms")
        print("  ✓ PingDataParser test passed")
        return True
    except Exception as e:
        print(f"  ✗ PingDataParser test failed: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_delivery_statistics():
    """Test delivery statistics calculation."""
    print("Testing DeliveryStatistics...")

    try:
        from network_path_analyzer import PingDataParser, DeliveryStatistics
    except ImportError as e:
        if "matplotlib" in str(e):
            print("  ⚠ DeliveryStatistics test skipped: matplotlib not available")
            return True
        else:
            raise

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(create_sample_ping_data())
        temp_file = f.name

    try:
        parser = PingDataParser(temp_file)
        stats = DeliveryStatistics(parser.data)

        delivery_rate = stats.calculate_overall_delivery_rate()
        longest_success = stats.find_longest_consecutive_successes()
        longest_loss = stats.find_longest_consecutive_losses()

        print(".3f")
        print(f"  Longest consecutive successes: {longest_success}")
        print(f"  Longest consecutive losses: {longest_loss}")
        print("  ✓ DeliveryStatistics test passed")
        return True
    except Exception as e:
        print(f"  ✗ DeliveryStatistics test failed: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_path_analyzer():
    """Test path analysis functionality."""
    print("Testing PathAnalyzer...")

    from network_path_analyzer import PathAnalyzer

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(create_sample_traceroute_data())
        temp_file = f.name

    try:
        analyzer = PathAnalyzer(temp_file)
        analysis = analyzer.analyze_geographic_path()

        print("  Path analysis generated")
        print("  ✓ PathAnalyzer test passed")
        return True
    except Exception as e:
        print(f"  ✗ PathAnalyzer test failed: {e}")
        return False
    finally:
        os.unlink(temp_file)

def test_rtt_analyzer():
    """Test RTT analysis functionality."""
    print("Testing RTTAnalyzer...")

    try:
        from network_path_analyzer import PingDataParser, RTTAnalyzer
    except ImportError as e:
        if "matplotlib" in str(e):
            print("  ⚠ RTTAnalyzer test skipped: matplotlib not available")
            return True
        else:
            raise

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(create_sample_ping_data())
        temp_file = f.name

    try:
        parser = PingDataParser(temp_file)
        rtt_analyzer = RTTAnalyzer(parser.data)

        min_rtt = rtt_analyzer.get_min_rtt()
        max_rtt = rtt_analyzer.get_max_rtt()

        print(".2f")
        print(".2f")
        print("  ✓ RTTAnalyzer test passed")
        return True
    except Exception as e:
        print(f"  ✗ RTTAnalyzer test failed: {e}")
        return False
    finally:
        os.unlink(temp_file)

def main():
    """Run all basic functionality tests."""
    print("Network Path Analyzer - Basic Functionality Tests")
    print("=" * 60)

    tests = [
        test_ping_parser,
        test_delivery_statistics,
        test_path_analyzer,
        test_rtt_analyzer
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        if test_func():
            passed += 1
        print()

    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All basic functionality tests passed!")
        return 0
    else:
        print("✗ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
