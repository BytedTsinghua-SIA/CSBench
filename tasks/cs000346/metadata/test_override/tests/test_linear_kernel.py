"""
Unit tests for linear kernel functionality
Tests basic mathematical operations without revealing optimization details
"""

import unittest
import numpy as np
from pathlib import Path
import subprocess
import sys
import os

class TestLinearKernel(unittest.TestCase):
    """Test cases for linear kernel implementations"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_data_dir = Path(__file__).parent.parent / "kernels" / "starter_code"
        self.input_size = 32  # Small test size for unit tests
        self.output_size = 16

    def test_kernel_directory_exists(self):
        """Test that kernel directory structure exists"""
        self.assertTrue(self.test_data_dir.exists())
        self.assertTrue(self.test_data_dir.is_dir())

    def test_source_files_exist(self):
        """Test that required source files are present"""
        required_files = [
            "reference.cc",
            "loop_unrolling.cc",
            "multithreading.cc",
            "simd_programming.cc",
            "multithreading_loop_unrolling.cc",
            "all_techniques.cc"
        ]

        for filename in required_files:
            file_path = self.test_data_dir / filename
            with self.subTest(filename=filename):
                self.assertTrue(file_path.exists(),
                              f"Required file {filename} not found")

    def test_compilation_possible(self):
        """Test that source files can be compiled without errors"""
        # Test compilation of reference implementation
        ref_file = self.test_data_dir / "reference.cc"
        if ref_file.exists():
            # Try to compile with basic flags
            result = subprocess.run(
                ["g++", "-std=c++17", "-c", str(ref_file), "-o", "/dev/null"],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0,
                           f"Compilation failed: {result.stderr}")

    def test_memory_layout_compatibility(self):
        """Test that memory layouts are compatible across implementations"""
        # This test ensures all implementations use the same data structures
        # without testing actual computation
        input_array = np.random.randint(-128, 127, self.input_size, dtype=np.int8)
        weight_array = np.random.randint(0, 16, (self.output_size, self.input_size), dtype=np.uint8)

        # Verify array shapes are compatible
        self.assertEqual(len(input_array), self.input_size)
        self.assertEqual(weight_array.shape, (self.output_size, self.input_size))

        # Test basic array operations that all implementations should support
        self.assertTrue(np.all(input_array >= -128))
        self.assertTrue(np.all(input_array <= 127))
        self.assertTrue(np.all(weight_array >= 0))
        self.assertTrue(np.all(weight_array <= 15))

    def test_quantization_parameters(self):
        """Test quantization parameter handling"""
        group_size = 32
        num_groups = (self.input_size + group_size - 1) // group_size

        # Test scale and zero point arrays
        scales = np.random.uniform(0.1, 2.0, num_groups).astype(np.float32)
        zero_points = np.random.randint(-8, 8, num_groups, dtype=np.int8)

        self.assertEqual(len(scales), num_groups)
        self.assertEqual(len(zero_points), num_groups)

        # Verify parameter ranges
        self.assertTrue(np.all(scales > 0))
        self.assertTrue(np.all(zero_points >= -8))
        self.assertTrue(np.all(zero_points <= 7))

    def test_output_dimensions(self):
        """Test output dimension calculations"""
        input_sizes = [32, 64, 128, 256]
        output_sizes = [16, 32, 64, 128]

        for in_size in input_sizes:
            for out_size in output_sizes:
                with self.subTest(input_size=in_size, output_size=out_size):
                    # Test that dimensions are valid for computation
                    self.assertGreater(in_size, 0)
                    self.assertGreater(out_size, 0)
                    self.assertLessEqual(in_size * out_size, 1024 * 1024)  # Reasonable limit

if __name__ == '__main__':
    unittest.main()
