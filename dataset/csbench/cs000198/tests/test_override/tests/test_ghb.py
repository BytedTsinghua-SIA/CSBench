#!/usr/bin/env python3
"""
Python unit tests for GHB prefetcher
Tests core functionality of C++ prefetcher implementation
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cpp_test_runner import run_cpp_test


class TestGHBPrefetcher(unittest.TestCase):
    """GHB prefetcher test class - tests C++ implementation"""
    
    def setUp(self):
        """Test setup"""
        self.test_name = 'ghb'
        self.cpp_test_file = 'test_ghb.cpp'
    
    def test_ghb_initialization(self):
        """Test GHB prefetcher initialization"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'ghb_initialization')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "GHB initialization test failed")
    
    def test_ghb_simple_stride(self):
        """Test GHB simple stride pattern detection"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'ghb_simple_stride')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "GHB simple stride test failed")
    
    def test_ghb_delta_correlation(self):
        """Test GHB delta correlation across different IPs"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'ghb_delta_correlation')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "GHB delta correlation test failed")
    
    def test_ghb_no_prefetch_for_store(self):
        """Test GHB does not prefetch for store operations"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'ghb_no_prefetch_for_store')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "GHB no prefetch for store test failed")
    
    def test_ghb_page_boundary_check(self):
        """Test GHB respects page boundaries"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'ghb_page_boundary_check')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "GHB page boundary check test failed")
    
    def test_ghb_cache_fill(self):
        """Test GHB cache fill handling"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'ghb_cache_fill')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "GHB cache fill test failed")
    
    def test_ghb_final_stats(self):
        """Test GHB final stats collection"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'ghb_final_stats')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "GHB final stats test failed")


if __name__ == '__main__':
    unittest.main()
