#!/usr/bin/env python3
"""
Python Unit Tests for Multicore and Cache Coherence
Each test method corresponds to a C test function in test_multicore.c
"""

import unittest
import subprocess
import os
import sys


class TestMulticore(unittest.TestCase):
    """Unit tests for multicore system and MESI cache coherence"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        # test_multicore should be in the parent directory (src/)
        cls.src_dir = os.path.dirname(cls.test_dir)
        cls.test_binary = os.path.join(cls.src_dir, "test_multicore")

        if not os.path.exists(cls.test_binary):
            raise FileNotFoundError(
                f"Test binary {cls.test_binary} not found. "
                "Please run 'make test_multicore' first."
            )

    def run_c_test(self, test_number):
        """
        Run a specific C test by test number

        Args:
            test_number: Test number (1-10)

        Returns:
            tuple: (return_code, stdout, stderr)
        """
        cmd = [self.test_binary, str(test_number)]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.src_dir,
            text=True,
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    def test_multicore_init(self):
        """
        Test 1: Multicore Initialization
        Corresponds to test_multicore_init() in C
        Verifies that all 4 CPUs are properly initialized
        """
        return_code, stdout, stderr = self.run_c_test(1)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout, "Test should output 'PASS' message")
        self.assertIn("All CPUs initialized correctly", stdout)

    def test_l1_cache_basic(self):
        """
        Test 2: L1 Cache Basic Access
        Corresponds to test_l1_cache_basic() in C
        Tests basic L1 cache read and write operations
        """
        return_code, stdout, stderr = self.run_c_test(2)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("L1 cache write and read successful", stdout)

    def test_mesi_exclusive(self):
        """
        Test 3: MESI Exclusive State
        Corresponds to test_mesi_exclusive() in C
        Verifies that a cache block enters Exclusive state after a read
        """
        return_code, stdout, stderr = self.run_c_test(3)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("Block in Exclusive state after read", stdout)

    def test_mesi_shared(self):
        """
        Test 4: MESI Shared State
        Corresponds to test_mesi_shared() in C
        Tests that when multiple CPUs read the same block,
        both caches enter Shared state
        """
        return_code, stdout, stderr = self.run_c_test(4)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("Both caches in Shared state", stdout)

    def test_mesi_modified(self):
        """
        Test 5: MESI Modified State
        Corresponds to test_mesi_modified() in C
        Verifies that a cache block is upgraded to Modified state after a write
        """
        return_code, stdout, stderr = self.run_c_test(5)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("Block upgraded to Modified state after write", stdout)

    def test_mesi_invalidation(self):
        """
        Test 6: MESI Invalidation
        Corresponds to test_mesi_invalidation() in C
        Tests that when one CPU writes to a block,
        other CPUs' copies are invalidated
        """
        return_code, stdout, stderr = self.run_c_test(6)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("CPU 1 cache invalidated when CPU 0 writes", stdout)

    def test_l1_mshr(self):
        """
        Test 7: L1 MSHR Functionality
        Corresponds to test_l1_mshr() in C
        Verifies that L1 MSHRs are properly allocated and released
        """
        return_code, stdout, stderr = self.run_c_test(7)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("L1 MSHR allocated and released correctly", stdout)

    def test_multicore_independence(self):
        """
        Test 8: Multicore Register Independence
        Corresponds to test_multicore_independence() in C
        Ensures that each CPU has an independent register file
        """
        return_code, stdout, stderr = self.run_c_test(8)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("Each CPU has independent register file", stdout)

    def test_l2_cache_dirty_bit(self):
        """
        Test 9: L2 Cache Dirty Bit
        Corresponds to test_l2_cache_dirty_bit() in C
        Tests that the L2 cache dirty bit is properly set when data is written
        """
        return_code, stdout, stderr = self.run_c_test(9)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("L2 cache dirty bit functionality", stdout)

    def test_instruction_cache(self):
        """
        Test 10: L1 Instruction Cache
        Corresponds to test_instruction_cache() in C
        Verifies that the instruction cache works correctly
        """
        return_code, stdout, stderr = self.run_c_test(10)

        self.assertEqual(
            return_code,
            0,
            f"Test failed with return code {return_code}\n"
            f"stdout: {stdout}\nstderr: {stderr}",
        )

        self.assertIn("PASS", stdout)
        self.assertIn("Instruction cache working correctly", stdout)


def run_all_tests():
    """Run all C tests at once to verify they all pass"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    # test_multicore should be in the parent directory (src/)
    src_dir = os.path.dirname(test_dir)
    test_binary = os.path.join(src_dir, "test_multicore")

    if not os.path.exists(test_binary):
        print(f"Error: Test binary {test_binary} not found.")
        print("Please run 'make test_multicore' first.")
        return False

    process = subprocess.Popen(
        [test_binary],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=src_dir,
        text=True,
    )
    stdout, stderr = process.communicate()

    print(stdout)
    if stderr:
        print("STDERR:", stderr, file=sys.stderr)

    return process.returncode == 0


if __name__ == "__main__":
    # Run Python unit tests
    unittest.main(verbosity=2, exit=False)

    # Also run all C tests together to show summary
    print("\n" + "=" * 60)
    print("Running all C tests together:")
    print("=" * 60)
    run_all_tests()
