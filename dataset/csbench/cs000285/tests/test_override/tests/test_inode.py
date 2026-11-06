"""
Unit tests for inode functionality.
Tests inode creation, serialization, and encrypted content reading.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import pickle

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

from secfs.types import User
from secfs.store.inode import Inode
import secfs.store.block
import secfs.crypto


class TestInode(unittest.TestCase):
    """Test inode operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.user1 = User(1)

    def test_inode_creation(self):
        """Test that Inode can be created with default values."""
        inode = Inode()
        
        self.assertEqual(inode.size, 0)
        self.assertEqual(inode.kind, 0)
        self.assertFalse(inode.ex)
        self.assertEqual(inode.blocks, [])
        self.assertIsNone(inode.encryption_metadata)

    def test_inode_serialization(self):
        """Test that Inode can be serialized and deserialized."""
        inode = Inode()
        inode.size = 100
        inode.kind = 1
        inode.blocks = [b"block1", b"block2"]
        
        serialized = inode.bytes()
        deserialized = pickle.loads(serialized)
        
        self.assertEqual(deserialized['size'], 100)
        self.assertEqual(deserialized['kind'], 1)
        self.assertEqual(deserialized['blocks'], [b"block1", b"block2"])

    @patch('secfs.store.block.load')
    def test_inode_load(self, mock_load):
        """Test that Inode can be loaded from a hash."""
        inode_data = {
            'size': 50,
            'kind': 1,
            'ex': False,
            'ctime': 1000,
            'mtime': 1000,
            'blocks': [b"block1"],
            'encryption_metadata': None
        }
        mock_load.return_value = pickle.dumps(inode_data)
        
        inode = Inode.load(b"inode_hash")
        
        self.assertIsNotNone(inode)
        self.assertEqual(inode.size, 50)
        self.assertEqual(inode.kind, 1)

    @patch('secfs.store.block.load')
    def test_inode_load_returns_none_when_missing(self, mock_load):
        """Test that Inode.load returns None when block is missing."""
        mock_load.return_value = None
        
        inode = Inode.load(b"inode_hash")
        
        self.assertIsNone(inode)

    @patch('secfs.store.block.load')
    def test_inode_read_plaintext(self, mock_load):
        """Test that Inode.read returns plaintext content."""
        inode = Inode()
        inode.blocks = [b"block1", b"block2"]
        mock_load.side_effect = [b"content1", b"content2"]
        
        content = inode.read()
        
        self.assertEqual(content, b"content1content2")

    @patch('secfs.store.block.load')
    @patch('secfs.crypto.decrypt_file_content')
    def test_inode_read_encrypted(self, mock_decrypt, mock_load):
        """Test that Inode.read decrypts encrypted content."""
        inode = Inode()
        inode.blocks = [b"encrypted_block"]
        inode.encryption_metadata = b"metadata_hash"
        mock_load.return_value = b"encrypted_data"
        mock_decrypt.return_value = b"decrypted_content"
        
        content = inode.read(user=self.user1)
        
        self.assertEqual(content, b"decrypted_content")
        mock_decrypt.assert_called_once_with(
            b"encrypted_data", b"metadata_hash", self.user1
        )

    @patch('secfs.store.block.load')
    def test_inode_read_encrypted_no_user(self, mock_load):
        """Test that Inode.read raises error for encrypted file without user."""
        inode = Inode()
        inode.blocks = [b"encrypted_block"]
        inode.encryption_metadata = b"metadata_hash"
        mock_load.return_value = b"encrypted_data"
        
        with self.assertRaises(PermissionError):
            inode.read()

    @patch('secfs.store.block.load')
    def test_inode_load_backward_compatibility(self, mock_load):
        """Test that Inode.load handles old inodes without encryption_metadata."""
        inode_data = {
            'size': 50,
            'kind': 1,
            'ex': False,
            'ctime': 1000,
            'mtime': 1000,
            'blocks': [b"block1"]
            # No encryption_metadata field
        }
        mock_load.return_value = pickle.dumps(inode_data)
        
        inode = Inode.load(b"inode_hash")
        
        self.assertIsNotNone(inode)
        self.assertIsNone(inode.encryption_metadata)


if __name__ == '__main__':
    unittest.main()

