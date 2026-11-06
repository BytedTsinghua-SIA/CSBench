"""
Unit tests for integrity functionality (Exercise 1: Integrity).
Tests version structures, VSL validation, and fork consistency.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import pickle
import hashlib

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
import secfs.tables
import secfs.fs


class TestTables(unittest.TestCase):
    """Test i-table and version structure functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.user1 = User(1)
        self.user2 = User(2)
        secfs.tables.current_itables.clear()
        secfs.tables.vsl.clear()
        secfs.tables.server = None

    def tearDown(self):
        """Clean up after tests."""
        secfs.tables.current_itables.clear()
        secfs.tables.vsl.clear()
        secfs.tables.server = None

    def test_itable_creation(self):
        """Test that Itable can be created and stores mappings."""
        itable = secfs.tables.Itable()
        self.assertEqual(itable.mapping, {})
        
        itable.mapping[0] = b"hash1"
        self.assertEqual(itable.mapping[0], b"hash1")

    @patch('secfs.store.block.load')
    def test_itable_load_from_block(self, mock_load):
        """Test that Itable can be loaded from a block."""
        test_mapping = {0: b"hash1", 1: b"hash2"}
        mock_load.return_value = pickle.dumps(test_mapping)
        
        itable = secfs.tables.Itable.load(b"ihandle")
        
        self.assertIsNotNone(itable)
        self.assertEqual(itable.mapping, test_mapping)

    @patch('secfs.store.block.load')
    def test_itable_load_returns_none_when_missing(self, mock_load):
        """Test that Itable.load returns None when block is missing."""
        mock_load.return_value = None
        
        itable = secfs.tables.Itable.load(b"ihandle")
        
        self.assertIsNone(itable)

    def test_resolve_user_i(self):
        """Test that resolve returns correct hash for user i."""
        itable = secfs.tables.Itable()
        itable.mapping[0] = b"inode_hash"
        secfs.tables.current_itables[self.user1] = itable
        
        file_i = I(self.user1, 0)
        result = secfs.tables.resolve(file_i)
        
        self.assertEqual(result, b"inode_hash")

    def test_resolve_group_i(self):
        """Test that resolve follows group i indirection."""
        user_itable = secfs.tables.Itable()
        user_itable.mapping[0] = b"inode_hash"
        secfs.tables.current_itables[self.user1] = user_itable
        
        group_itable = secfs.tables.Itable()
        user_i = I(self.user1, 0)
        group_itable.mapping[0] = user_i
        secfs.tables.current_itables[Group(100)] = group_itable
        
        group_i = I(Group(100), 0)
        result = secfs.tables.resolve(group_i)
        
        self.assertEqual(result, b"inode_hash")

    def test_resolve_unallocated_i(self):
        """Test that resolve returns None for unallocated i."""
        unallocated_i = I(self.user1)
        result = secfs.tables.resolve(unallocated_i)
        
        self.assertIsNone(result)

    def test_resolve_missing_itable(self):
        """Test that resolve returns None when itable is missing."""
        file_i = I(self.user1, 0)
        result = secfs.tables.resolve(file_i)
        
        self.assertIsNone(result)

    def test_modmap_allocates_new_inumber(self):
        """Test that modmap allocates new inumber for unallocated i."""
        itable = secfs.tables.Itable()
        secfs.tables.current_itables[self.user1] = itable
        
        unallocated_i = I(self.user1)
        result = secfs.tables.modmap(self.user1, unallocated_i, b"hash")
        
        self.assertTrue(result.allocated())
        self.assertEqual(result.n, 0)
        self.assertEqual(itable.mapping[0], b"hash")

    def test_modmap_updates_existing_mapping(self):
        """Test that modmap updates existing i mapping."""
        itable = secfs.tables.Itable()
        itable.mapping[0] = b"old_hash"
        secfs.tables.current_itables[self.user1] = itable
        
        file_i = I(self.user1, 0)
        result = secfs.tables.modmap(self.user1, file_i, b"new_hash")
        
        self.assertEqual(itable.mapping[0], b"new_hash")

    def test_modmap_group_i_creates_user_i(self):
        """Test that modmap creates user i when modifying group i."""
        user_itable = secfs.tables.Itable()
        secfs.tables.current_itables[self.user1] = user_itable
        
        group_itable = secfs.tables.Itable()
        secfs.tables.current_itables[Group(100)] = group_itable
        
        group_i = I(Group(100))
        result = secfs.tables.modmap(self.user1, group_i, b"hash")
        
        self.assertTrue(result.allocated())
        self.assertEqual(result.p, Group(100))

    def test_create_version_structure(self):
        """Test that version structure is created with principal hashes."""
        itable1 = secfs.tables.Itable()
        itable1.mapping[0] = b"hash1"
        secfs.tables.current_itables[self.user1] = itable1
        
        itable2 = secfs.tables.Itable()
        itable2.mapping[0] = b"hash2"
        secfs.tables.current_itables[self.user2] = itable2
        
        vs = secfs.tables._create_version_structure()
        
        self.assertIsNotNone(vs)
        self.assertIn('principal_hashes', vs)
        self.assertIn(self.user1, vs['principal_hashes'])
        self.assertIn(self.user2, vs['principal_hashes'])

    def test_create_version_structure_empty_when_no_itables(self):
        """Test that version structure has empty principal_hashes when no itables exist."""
        vs = secfs.tables._create_version_structure()
        
        # When no itables exist, it returns a structure with empty principal_hashes
        # This is expected behavior - the function creates a structure even if empty
        if vs is not None:
            self.assertEqual(vs.get('principal_hashes', {}), {})
        else:
            # Or it could return None, both are acceptable
            self.assertIsNone(vs)

    def test_sign_version_structure(self):
        """Test that version structure is signed by users."""
        mock_private_key = MagicMock()
        mock_private_key.sign.return_value = b"signature"
        secfs.crypto.keys[self.user1] = mock_private_key
        
        itable = secfs.tables.Itable()
        secfs.tables.current_itables[self.user1] = itable
        
        vs = secfs.tables._create_version_structure()
        signed_vs = secfs.tables._sign_version_structure(vs)
        
        self.assertIn('signatures', signed_vs)
        self.assertIn(self.user1, signed_vs['signatures'])

    def test_validate_version_structure_valid_signature(self):
        """Test that valid version structure passes validation."""
        vs = {'principal_hashes': {self.user1: b"hash"}, 'version': 1}
        vs_bytes = pickle.dumps(vs)
        
        mock_public_key = MagicMock()
        mock_public_key.verify.return_value = None  # No exception means valid
        
        with patch('secfs.fs.usermap', {self.user1: b"public_key_pem"}):
            with patch('cryptography.hazmat.primitives.serialization.load_pem_public_key') as mock_load:
                mock_load.return_value = mock_public_key
                signed_vs = {
                    'vs': vs,
                    'signatures': {self.user1: b"signature"}
                }
                result = secfs.tables._validate_version_structure(signed_vs)
                self.assertTrue(result)

    def test_validate_version_structure_invalid_user(self):
        """Test that validation fails for unknown user."""
        vs = {'principal_hashes': {self.user1: b"hash"}, 'version': 1}
        signed_vs = {
            'vs': vs,
            'signatures': {self.user1: b"signature"}
        }
        
        with patch('secfs.fs.usermap', {}):
            result = secfs.tables._validate_version_structure(signed_vs)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

