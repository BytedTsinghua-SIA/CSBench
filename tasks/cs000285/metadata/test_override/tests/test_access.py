"""
Unit tests for access control functionality (Exercise 2: Group-permissions).
Tests permission checking for read and write operations.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys

# Mock cryptography before importing secfs modules
sys.modules['cryptography'] = MagicMock()
sys.modules['cryptography.hazmat'] = MagicMock()
sys.modules['cryptography.hazmat.primitives'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.asymmetric'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.asymmetric.padding'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.asymmetric.rsa'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.serialization'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.hashes'] = MagicMock()
sys.modules['cryptography.hazmat.backends'] = MagicMock()
sys.modules['cryptography.hazmat.backends.default_backend'] = MagicMock()
sys.modules['cryptography.fernet'] = MagicMock()

from secfs.types import User, Group, I
import secfs.access
import secfs.fs


class TestAccessControl(unittest.TestCase):
    """Test access control functions for read and write permissions."""

    def setUp(self):
        """Set up test fixtures."""
        self.user1 = User(1)
        self.user2 = User(2)
        self.group1 = Group(100)
        secfs.fs.groupmap.clear()
        secfs.fs.usermap.clear()

    def tearDown(self):
        """Clean up after tests."""
        secfs.fs.groupmap.clear()
        secfs.fs.usermap.clear()

    def test_can_read_user_owned_file(self):
        """Test that user can read their own file."""
        file_i = I(self.user1, 0)
        result = secfs.access.can_read(self.user1, file_i)
        self.assertTrue(result)

    def test_can_read_denies_other_user(self):
        """Test that user cannot read another user's file."""
        file_i = I(self.user1, 0)
        result = secfs.access.can_read(self.user2, file_i)
        self.assertFalse(result)

    @patch.dict('secfs.fs.groupmap', {Group(100): [User(1), User(2)]})
    def test_can_read_group_file_member(self):
        """Test that group member can read group file."""
        group = Group(100)
        file_i = I(group, 0)
        result = secfs.access.can_read(self.user1, file_i)
        self.assertTrue(result)

    @patch.dict('secfs.fs.groupmap', {Group(100): [User(1)]})
    def test_can_read_group_file_non_member(self):
        """Test that non-member cannot read group file."""
        group = Group(100)
        file_i = I(group, 0)
        result = secfs.access.can_read(self.user2, file_i)
        self.assertFalse(result)

    def test_can_write_user_owned_file(self):
        """Test that user can write their own file."""
        file_i = I(self.user1, 0)
        result = secfs.access.can_write(self.user1, file_i)
        self.assertTrue(result)

    def test_can_write_denies_other_user(self):
        """Test that user cannot write another user's file."""
        file_i = I(self.user1, 0)
        result = secfs.access.can_write(self.user2, file_i)
        self.assertFalse(result)

    @patch.dict('secfs.fs.groupmap', {Group(100): [User(1), User(2)]})
    def test_can_write_group_file_member(self):
        """Test that group member can write group file."""
        group = Group(100)
        file_i = I(group, 0)
        result = secfs.access.can_write(self.user1, file_i)
        self.assertTrue(result)

    @patch.dict('secfs.fs.groupmap', {Group(100): [User(1)]})
    def test_can_write_group_file_non_member(self):
        """Test that non-member cannot write group file."""
        group = Group(100)
        file_i = I(group, 0)
        result = secfs.access.can_write(self.user2, file_i)
        self.assertFalse(result)

    def test_can_read_invalid_user_type(self):
        """Test that can_read raises TypeError for invalid user type."""
        file_i = I(self.user1, 0)
        with self.assertRaises(TypeError):
            secfs.access.can_read("not_a_user", file_i)

    def test_can_write_invalid_user_type(self):
        """Test that can_write raises TypeError for invalid user type."""
        file_i = I(self.user1, 0)
        with self.assertRaises(TypeError):
            secfs.access.can_write("not_a_user", file_i)


if __name__ == '__main__':
    unittest.main()

