#!/usr/bin/env python3
"""
Python unit tests for FDP prefetcher
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cpp_test_runner import run_cpp_test


class TestFDPPrefetcher(unittest.TestCase):
    """FDP prefetcher test class - tests C++ implementation"""

    def setUp(self):
        """Test setup"""
        self.test_name = "fdp"
        self.cpp_test_file = "test_fdp.cpp"

    def test_fdp_initialization(self):
        """Test FDP prefetcher initialization"""
        success, results, output = run_cpp_test(
            self.test_name, self.cpp_test_file, "fdp_initialization"
        )
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if "error" in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "FDP initialization test failed")

    def test_fdp_stride_detection(self):
        """Test FDP stride pattern detection"""
        success, results, output = run_cpp_test(
            self.test_name, self.cpp_test_file, "fdp_stride_detection"
        )
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if "error" in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "FDP stride detection test failed")

    def test_fdp_aggressiveness_levels(self):
        """Test FDP aggressiveness level adjustment"""
        success, results, output = run_cpp_test(
            self.test_name, self.cpp_test_file, "fdp_aggressiveness_levels"
        )
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if "error" in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "FDP aggressiveness levels test failed")

    def test_fdp_feedback_mechanism(self):
        """Test FDP feedback mechanism"""
        success, results, output = run_cpp_test(
            self.test_name, self.cpp_test_file, "fdp_feedback_mechanism"
        )
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if "error" in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "FDP feedback mechanism test failed")

    def test_fdp_no_prefetch_for_store(self):
        """Test FDP does not prefetch for store operations"""
        success, results, output = run_cpp_test(
            self.test_name, self.cpp_test_file, "fdp_no_prefetch_for_store"
        )
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if "error" in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "FDP no prefetch for store test failed")

    def test_fdp_page_boundary_check(self):
        """Test FDP respects page boundaries"""
        success, results, output = run_cpp_test(
            self.test_name, self.cpp_test_file, "fdp_page_boundary_check"
        )
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if "error" in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "FDP page boundary check test failed")

    def test_fdp_cache_fill(self):
        """Test FDP cache fill handling"""
        success, results, output = run_cpp_test(
            self.test_name, self.cpp_test_file, "fdp_cache_fill"
        )
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if "error" in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "FDP cache fill test failed")

    def test_fdp_final_stats(self):
        """Test FDP final stats collection"""
        success, results, output = run_cpp_test(
            self.test_name, self.cpp_test_file, "fdp_final_stats"
        )
        if not success:
            print("\n" + "=" * 60)
            print("C++ Test Output:")
            print("=" * 60)
            print(output)
            print("=" * 60)
        if "error" in results:
            self.fail(f"C++ test execution failed: {results['error']}")
        self.assertTrue(success, "FDP final stats test failed")


if __name__ == "__main__":
    unittest.main()
