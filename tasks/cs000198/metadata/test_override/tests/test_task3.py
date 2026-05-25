#!/usr/bin/env python3
"""
Python unit tests for Task3 prefetcher
Tests core functionality of C++ prefetcher implementation
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cpp_test_runner import run_cpp_test


class TestTask3Prefetcher(unittest.TestCase):
    """Task3 prefetcher test class - tests C++ implementation"""
    
    def setUp(self):
        """Test setup"""
        self.test_name = 'task3'
        self.cpp_test_file = 'test_task3.cpp'
    
    def test_task3_initialization(self):
        """Test Task3 prefetcher initialization"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'task3_initialization')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "Task3 initialization test failed")
    
    def test_task3_stride_detection(self):
        """Test Task3 stride pattern detection"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'task3_stride_detection')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "Task3 stride detection test failed")
    
    def test_task3_confidence_mechanism(self):
        """Test Task3 confidence mechanism"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'task3_confidence_mechanism')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "Task3 confidence mechanism test failed")
    
    def test_task3_spatial_pattern(self):
        """Test Task3 spatial pattern detection"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'task3_spatial_pattern')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "Task3 spatial pattern test failed")
    
    def test_task3_no_prefetch_for_store(self):
        """Test Task3 does not prefetch for store operations"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'task3_no_prefetch_for_store')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "Task3 no prefetch for store test failed")
    
    def test_task3_page_boundary_check(self):
        """Test Task3 respects page boundaries"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'task3_page_boundary_check')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "Task3 page boundary check test failed")
    
    def test_task3_cache_fill(self):
        """Test Task3 cache fill handling"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'task3_cache_fill')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "Task3 cache fill test failed")
    
    def test_task3_final_stats(self):
        """Test Task3 final stats collection"""
        success, results, output = run_cpp_test(self.test_name, self.cpp_test_file, 'task3_final_stats')
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if 'error' in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "Task3 final stats test failed")


if __name__ == '__main__':
    unittest.main()
