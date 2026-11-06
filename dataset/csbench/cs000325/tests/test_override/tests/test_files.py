import unittest
from unittest.mock import Mock
import string
from afs import files


class TestFiles(unittest.TestCase):
    """Test cases for the files class"""

    def test_init_with_valid_numfiles(self):
        """Test initialization with valid number of files"""
        f = files(3)
        expected_files = list(string.ascii_lowercase)[:3]
        self.assertEqual(f.numfiles, 3)
        self.assertEqual(f.getfiles(), expected_files)

    def test_init_with_zero_files(self):
        """Test initialization with zero files"""
        f = files(0)
        self.assertEqual(f.numfiles, 0)
        self.assertEqual(f.getfiles(), [])

    def test_init_with_max_files(self):
        """Test initialization with maximum supported files"""
        f = files(26)
        expected_files = list(string.ascii_lowercase)
        self.assertEqual(f.numfiles, 26)
        self.assertEqual(f.getfiles(), expected_files)

    def test_getvalue_sequence(self):
        """Test that getvalue returns sequential values"""
        f = files(1)
        first_value = f.getvalue()
        second_value = f.getvalue()
        third_value = f.getvalue()

        self.assertEqual(first_value, 0)
        self.assertEqual(second_value, 1)
        self.assertEqual(third_value, 2)

    def test_getfiles_returns_copy(self):
        """Test that getfiles returns a copy, not the original list"""
        f = files(2)
        files_list1 = f.getfiles()
        files_list2 = f.getfiles()

        self.assertEqual(files_list1, files_list2)
        # Modify one list and ensure the other is not affected
        if files_list1:
            files_list1[0] = 'modified'
            self.assertNotEqual(files_list1, files_list2)
