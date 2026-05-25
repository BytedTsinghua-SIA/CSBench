"""
Unit tests for cryptographic functionality (Exercise 3: Read-permissions).
Tests file encryption, decryption, and key distribution.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
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

from secfs.types import User, Group
import secfs.crypto
import secfs.fs
import secfs.store.block


class TestCrypto(unittest.TestCase):
    """Test cryptographic functions for file encryption and key distribution."""

    def setUp(self):
        """Set up test fixtures."""
        self.user1 = User(1)
        self.user2 = User(2)
        self.group1 = Group(100)
        secfs.fs.groupmap.clear()
        secfs.fs.usermap.clear()
        secfs.crypto.keys.clear()

    def tearDown(self):
        """Clean up after tests."""
        secfs.fs.groupmap.clear()
        secfs.fs.usermap.clear()
        secfs.crypto.keys.clear()

    @patch('secfs.store.block.store')
    def test_encrypt_file_content_creates_metadata(self, mock_store):
        """Test that encrypt_file_content creates encryption metadata."""
        mock_store.return_value = b"metadata_hash"
        test_data = b"test content"
        
        encrypted_data, metadata_hash = secfs.crypto.encrypt_file_content(
            test_data, self.user1
        )
        
        self.assertIsNotNone(metadata_hash)
        self.assertNotEqual(encrypted_data, test_data)

    @patch('secfs.store.block.store')
    def test_encrypt_file_content_encrypts_for_owner(self, mock_store):
        """Test that encryption includes owner's encrypted key."""
        mock_private_key = MagicMock()
        mock_public_key = MagicMock()
        mock_private_key.public_key.return_value = mock_public_key
        mock_public_key.encrypt.return_value = b"encrypted_key"
        secfs.crypto.keys[self.user1] = mock_private_key
        
        mock_store.return_value = b"metadata_hash"
        test_data = b"test content"
        
        encrypted_data, metadata_hash = secfs.crypto.encrypt_file_content(
            test_data, self.user1
        )
        
        mock_public_key.encrypt.assert_called_once()

    @patch('secfs.store.block.store')
    @patch('secfs.store.block.load')
    def test_decrypt_file_content_with_valid_key(self, mock_load, mock_store):
        """Test that decrypt_file_content works with valid encryption metadata."""
        # Setup encryption
        mock_private_key = MagicMock()
        mock_public_key = MagicMock()
        mock_private_key.public_key.return_value = mock_public_key
        mock_public_key.encrypt.return_value = b"encrypted_sym_key"
        secfs.crypto.keys[self.user1] = mock_private_key
        
        test_data = b"original content"
        encrypted_data, metadata_hash = secfs.crypto.encrypt_file_content(
            test_data, self.user1
        )
        
        # Setup decryption
        import pickle
        metadata = {
            'encrypted_keys': {self.user1: b"encrypted_sym_key"},
            'owner': self.user1,
            'group': None
        }
        mock_load.return_value = pickle.dumps(metadata)
        mock_private_key.decrypt.return_value = b"sym_key_bytes"
        
        # Mock Fernet decryption
        with patch('secfs.crypto.decrypt_sym') as mock_decrypt:
            mock_decrypt.return_value = test_data
            result = secfs.crypto.decrypt_file_content(
                encrypted_data, metadata_hash, self.user1
            )
            self.assertEqual(result, test_data)

    @patch('secfs.store.block.load')
    def test_decrypt_file_content_unauthorized_user(self, mock_load):
        """Test that decrypt_file_content raises error for unauthorized user."""
        import pickle
        metadata = {
            'encrypted_keys': {self.user1: b"encrypted_key"},
            'owner': self.user1,
            'group': None
        }
        mock_load.return_value = pickle.dumps(metadata)
        
        with self.assertRaises(PermissionError):
            secfs.crypto.decrypt_file_content(
                b"encrypted_data", b"metadata_hash", self.user2
            )

    @patch('secfs.store.block.store')
    @patch.dict('secfs.fs.groupmap', {Group(100): [User(1), User(2)]})
    def test_encrypt_file_content_for_group(self, mock_store):
        """Test that encryption includes group members' keys."""
        mock_private_key1 = MagicMock()
        mock_public_key1 = MagicMock()
        mock_private_key1.public_key.return_value = mock_public_key1
        mock_public_key1.encrypt.return_value = b"encrypted_key1"
        secfs.crypto.keys[self.user1] = mock_private_key1
        
        mock_private_key2 = MagicMock()
        mock_public_key2 = MagicMock()
        mock_private_key2.public_key.return_value = mock_public_key2
        mock_public_key2.encrypt.return_value = b"encrypted_key2"
        secfs.crypto.keys[self.user2] = mock_private_key2
        
        mock_store.return_value = b"metadata_hash"
        test_data = b"test content"
        
        encrypted_data, metadata_hash = secfs.crypto.encrypt_file_content(
            test_data, self.user1, self.group1
        )
        
        # Owner and group members should have encrypted keys
        # Owner is user1, so user1's key is encrypted once for owner, once for group member
        # Actually, owner is only encrypted once, and group members are encrypted separately
        self.assertGreaterEqual(mock_public_key1.encrypt.call_count, 1)
        self.assertGreaterEqual(mock_public_key2.encrypt.call_count, 1)

    def test_is_encrypted_returns_false_for_none(self):
        """Test that is_encrypted returns False for None."""
        result = secfs.crypto.is_encrypted(None)
        self.assertFalse(result)

    @patch('secfs.store.block.load')
    def test_is_encrypted_returns_true_when_metadata_exists(self, mock_load):
        """Test that is_encrypted returns True when metadata exists."""
        mock_load.return_value = b"metadata"
        result = secfs.crypto.is_encrypted(b"hash")
        self.assertTrue(result)

    @patch('secfs.store.block.load')
    def test_is_encrypted_returns_false_when_metadata_missing(self, mock_load):
        """Test that is_encrypted returns False when metadata is missing."""
        mock_load.return_value = None
        result = secfs.crypto.is_encrypted(b"hash")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

