"""
Unit tests for file system operations.
Tests file creation, reading, writing with permissions and encryption.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import time

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
import secfs.fs
import secfs.store.block
import secfs.store.tree
import secfs.tables
import secfs.access


class TestFileSystem(unittest.TestCase):
    """Test file system operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.user1 = User(1)
        self.user2 = User(2)
        self.group1 = Group(100)
        secfs.fs.groupmap.clear()
        secfs.fs.usermap.clear()
        secfs.tables.current_itables.clear()

    def tearDown(self):
        """Clean up after tests."""
        secfs.fs.groupmap.clear()
        secfs.fs.usermap.clear()
        secfs.tables.current_itables.clear()

    @patch('secfs.store.block.store')
    @patch('secfs.tables.modmap')
    @patch('secfs.store.tree.add')
    @patch('secfs.access.can_write')
    def test_create_file(self, mock_can_write, mock_add, mock_modmap, mock_store):
        """Test that create_file creates a new file inode."""
        mock_can_write.return_value = True
        mock_store.return_value = b"inode_hash"
        mock_modmap.return_value = I(self.user1, 0)
        mock_add.return_value = b"dir_hash"
        
        parent_i = I(self.user1, 0)
        file_i = secfs.fs.create(parent_i, b"test.txt", self.user1, self.user1)
        
        self.assertIsNotNone(file_i)
        mock_store.assert_called()

    @patch('secfs.store.block.store')
    @patch('secfs.tables.modmap')
    @patch('secfs.store.tree.add')
    @patch('secfs.access.can_write')
    def test_create_directory(self, mock_can_write, mock_add, mock_modmap, mock_store):
        """Test that mkdir creates a new directory with . and .. entries."""
        mock_can_write.return_value = True
        mock_store.return_value = b"inode_hash"
        mock_modmap.return_value = I(self.user1, 0)
        mock_add.return_value = b"dir_hash"
        
        parent_i = I(self.user1, 0)
        dir_i = secfs.fs.mkdir(parent_i, b"testdir", self.user1, self.user1)
        
        self.assertIsNotNone(dir_i)
        # Should add . and .. entries, plus link() also calls add
        self.assertGreaterEqual(mock_add.call_count, 2)

    @patch('secfs.store.block.store')
    @patch('secfs.tables.modmap')
    @patch('secfs.store.tree.add')
    @patch('secfs.access.can_write')
    def test_create_group_file(self, mock_can_write, mock_add, mock_modmap, mock_store):
        """Test that create can create a file owned by a group."""
        mock_can_write.return_value = True
        mock_store.return_value = b"inode_hash"
        user_i = I(self.user1, 0)
        group_i = I(self.group1, 0)
        # modmap is called multiple times: for user_i, for group_i, and in link()
        mock_modmap.side_effect = [user_i, group_i, I(self.user1, 0)]
        mock_add.return_value = b"dir_hash"
        
        secfs.fs.groupmap[self.group1] = [self.user1, self.user2]
        parent_i = I(self.user1, 0)
        
        file_i = secfs.fs.create(parent_i, b"test.txt", self.user1, self.group1)
        
        self.assertEqual(file_i.p, self.group1)

    @patch('secfs.store.block.load')
    @patch('secfs.tables.resolve')
    @patch('secfs.access.can_read')
    def test_read_file(self, mock_can_read, mock_resolve, mock_load):
        """Test that read returns file content."""
        mock_can_read.return_value = True
        mock_resolve.return_value = b"inode_hash"
        
        mock_inode = MagicMock()
        mock_inode.read.return_value = b"file content"
        
        with patch('secfs.fs.get_inode', return_value=mock_inode):
            file_i = I(self.user1, 0)
            content = secfs.fs.read(self.user1, file_i, 0, 13)
            
            self.assertEqual(content, b"file content")

    @patch('secfs.store.block.load')
    @patch('secfs.tables.resolve')
    @patch('secfs.access.can_read')
    def test_read_file_denied_permission(self, mock_can_read, mock_resolve, mock_load):
        """Test that read raises PermissionError when access denied."""
        mock_can_read.return_value = False
        file_i = I(self.user1, 0)
        
        with self.assertRaises(PermissionError):
            secfs.fs.read(self.user2, file_i, 0, 10)

    @patch('secfs.store.block.store')
    @patch('secfs.store.block.load')
    @patch('secfs.tables.resolve')
    @patch('secfs.tables.modmap')
    @patch('secfs.access.can_write')
    def test_write_file(self, mock_can_write, mock_modmap, mock_resolve, mock_load, mock_store):
        """Test that write updates file content."""
        mock_can_write.return_value = True
        mock_resolve.return_value = b"inode_hash"
        mock_store.return_value = b"new_hash"
        
        mock_inode = MagicMock()
        mock_inode.read.return_value = b"old content"
        mock_inode.encryption_metadata = None
        mock_inode.blocks = [b"block_hash"]
        
        with patch('secfs.fs.get_inode', return_value=mock_inode):
            file_i = I(self.user1, 0)
            written = secfs.fs.write(self.user1, file_i, 0, b"new")
            
            self.assertEqual(written, 3)
            mock_store.assert_called()

    @patch('secfs.store.block.store')
    @patch('secfs.store.block.load')
    @patch('secfs.tables.resolve')
    @patch('secfs.access.can_write')
    def test_write_encrypted_file(self, mock_can_write, mock_resolve, mock_load, mock_store):
        """Test that write re-encrypts encrypted file content."""
        mock_can_write.return_value = True
        mock_resolve.return_value = b"inode_hash"
        mock_store.side_effect = [b"encrypted_data", b"metadata_hash", b"new_inode_hash"]
        
        import pickle
        metadata = {
            'encrypted_keys': {self.user1: b"encrypted_key"},
            'owner': self.user1,
            'group': None
        }
        mock_load.return_value = pickle.dumps(metadata)
        
        mock_inode = MagicMock()
        mock_inode.read.return_value = b"decrypted content"
        mock_inode.encryption_metadata = b"metadata_hash"
        mock_inode.blocks = [b"encrypted_block"]
        
        with patch('secfs.fs.get_inode', return_value=mock_inode):
            with patch('secfs.crypto.encrypt_file_content') as mock_encrypt:
                mock_encrypt.return_value = (b"new_encrypted", b"new_metadata")
                with patch('secfs.tables.modmap'):
                    file_i = I(self.user1, 0)
                    secfs.fs.write(self.user1, file_i, 0, b"new")
                    
                    mock_encrypt.assert_called_once()

    @patch('secfs.store.block.store')
    @patch('secfs.tables.modmap')
    @patch('secfs.store.tree.add')
    @patch('secfs.access.can_write')
    def test_create_encrypted_file(self, mock_can_write, mock_add, mock_modmap, mock_store):
        """Test that create can create an encrypted file."""
        mock_can_write.return_value = True
        mock_store.side_effect = [b"encrypted_data", b"metadata_hash", b"inode_hash"]
        mock_modmap.return_value = I(self.user1, 0)
        mock_add.return_value = b"dir_hash"
        
        with patch('secfs.crypto.encrypt_file_content') as mock_encrypt:
            mock_encrypt.return_value = (b"encrypted_data", b"metadata_hash")
            parent_i = I(self.user1, 0)
            file_i = secfs.fs._create(parent_i, b"secret.txt", self.user1, self.user1, False, encrypted=True)
            
            mock_encrypt.assert_called_once()

    @patch('secfs.store.block.load')
    @patch('secfs.tables.resolve')
    @patch('secfs.access.can_read')
    def test_read_encrypted_file(self, mock_can_read, mock_resolve, mock_load):
        """Test that read decrypts encrypted file content."""
        mock_can_read.return_value = True
        mock_resolve.return_value = b"inode_hash"
        
        mock_inode = MagicMock()
        mock_inode.encryption_metadata = b"metadata_hash"
        mock_inode.blocks = [b"encrypted_block"]
        mock_inode.read.return_value = b"decrypted content"
        
        with patch('secfs.fs.get_inode', return_value=mock_inode):
            file_i = I(self.user1, 0)
            content = secfs.fs.read(self.user1, file_i, 0, 10)
            
            self.assertEqual(content, b"decrypted ")


if __name__ == '__main__':
    unittest.main()

