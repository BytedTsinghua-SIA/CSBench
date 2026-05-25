import unittest
from afs import filedesc


class TestFiledesc(unittest.TestCase):
    """Test cases for the filedesc class"""

    def test_init_filedesc(self):
        """Test filedesc initialization"""
        fd = filedesc()
        self.assertEqual(fd.max, 1024)
        # Check that all file descriptors are initialized to empty string
        for i in range(fd.max):
            self.assertEqual(fd.fd[i], "")

    def test_init_with_custom_max(self):
        """Test filedesc initialization with custom max"""
        fd = filedesc(512)
        self.assertEqual(fd.max, 512)
        for i in range(fd.max):
            self.assertEqual(fd.fd[i], "")

    def test_alloc_sequential(self):
        """Test sequential file descriptor allocation"""
        fd = filedesc(5)

        # Allocate first available descriptor
        result = fd.alloc("test.txt")
        self.assertEqual(result, 0)
        self.assertEqual(fd.fd[0], "test.txt")

        # Allocate next available descriptor
        result = fd.alloc("another.txt")
        self.assertEqual(result, 1)
        self.assertEqual(fd.fd[1], "another.txt")

    def test_alloc_specific_descriptor(self):
        """Test allocation of specific file descriptor"""
        fd = filedesc(5)

        result = fd.alloc("test.txt", 3)
        self.assertEqual(result, 3)
        self.assertEqual(fd.fd[3], "test.txt")

    def test_alloc_descriptor_already_in_use(self):
        """Test allocation of already used descriptor"""
        fd = filedesc(5)
        fd.alloc("first.txt", 2)

        with self.assertRaises(SystemExit):
            fd.alloc("second.txt", 2)

    def test_alloc_beyond_max(self):
        """Test allocation when all descriptors are used"""
        fd = filedesc(2)
        fd.alloc("file1.txt", 0)
        fd.alloc("file2.txt", 1)

        # All descriptors are now used
        result = fd.alloc("file3.txt")
        self.assertEqual(result, -1)

    def test_lookup_valid_descriptor(self):
        """Test lookup of valid file descriptor"""
        fd = filedesc(5)
        fd.alloc("test.txt", 2)

        result = fd.lookup(2)
        self.assertEqual(result, "test.txt")

    def test_lookup_invalid_descriptor_range(self):
        """Test lookup with descriptor out of range"""
        fd = filedesc(5)

        with self.assertRaises(SystemExit):
            fd.lookup(-1)

        with self.assertRaises(SystemExit):
            fd.lookup(5)

    def test_lookup_unused_descriptor(self):
        """Test lookup of unused file descriptor"""
        fd = filedesc(5)

        with self.assertRaises(SystemExit):
            fd.lookup(2)

    def test_free_descriptor(self):
        """Test freeing a file descriptor"""
        fd = filedesc(5)
        fd.alloc("test.txt", 2)
        self.assertEqual(fd.fd[2], "test.txt")

        fd.free(2)
        self.assertEqual(fd.fd[2], "")

    def test_free_invalid_descriptor_range(self):
        """Test freeing descriptor out of range"""
        fd = filedesc(5)

        with self.assertRaises(SystemExit):
            fd.free(-1)

        with self.assertRaises(SystemExit):
            fd.free(5)

    def test_free_unused_descriptor(self):
        """Test freeing already unused descriptor"""
        fd = filedesc(5)

        with self.assertRaises(SystemExit):
            fd.free(2)
