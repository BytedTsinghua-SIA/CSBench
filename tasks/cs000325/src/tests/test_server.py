import unittest
from unittest.mock import Mock, patch
from afs import server


class TestServer(unittest.TestCase):
    """Test cases for the server class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_files = Mock()
        self.mock_files.getfiles.return_value = ['a', 'b']
        self.mock_files.getvalue.side_effect = [0, 1]

    def test_init_server(self):
        """Test server initialization"""
        s = server(self.mock_files, False, 0)

        self.assertEqual(s.files, self.mock_files)
        self.assertFalse(s.solve)
        self.assertEqual(s.detail, 0)
        self.assertEqual(s.getcnt, 0)
        self.assertEqual(s.putcnt, 0)
        self.assertEqual(s.contents, {'a': 0, 'b': 1})

    def test_get_operation(self):
        """Test server get operation"""
        s = server(self.mock_files, True, 1)
        mock_client = Mock()
        mock_client.getname.return_value = 'c0'

        # Set clients to initialize cache
        s.setclients([mock_client])

        result = s.get('c0', 'a')
        self.assertEqual(result, 0)
        self.assertEqual(s.getcnt, 1)
        self.assertIn('c0', s.cache)
        self.assertIn('a', s.cache['c0'])

    def test_get_nonexistent_file(self):
        """Test get operation with nonexistent file"""
        s = server(self.mock_files, False, 0)

        with self.assertRaises(SystemExit):
            s.get('c0', 'nonexistent')

    def test_put_operation(self):
        """Test server put operation"""
        s = server(self.mock_files, True, 1)
        mock_client = Mock()
        mock_client.getname.return_value = 'c0'

        # Set up initial state
        s.clients = [mock_client]
        s.cache = {'c0': ['a']}

        s.put('c0', 'a', 42)
        self.assertEqual(s.putcnt, 1)
        self.assertEqual(s.contents['a'], 42)

    def test_put_nonexistent_file(self):
        """Test put operation with nonexistent file"""
        s = server(self.mock_files, False, 0)

        with self.assertRaises(SystemExit):
            s.put('c0', 'nonexistent', 42)

    def test_callback_invalidation(self):
        """Test callback invalidation when file is put"""
        s = server(self.mock_files, True, 2)
        mock_client1 = Mock()
        mock_client1.getname.return_value = 'c0'
        mock_client2 = Mock()
        mock_client2.getname.return_value = 'c1'

        s.clients = [mock_client1, mock_client2]
        s.cache = {'c0': ['a'], 'c1': ['a']}

        # Mock invalidate method
        mock_client1.invalidate = Mock()

        s.put('c1', 'a', 42)

        # Should call invalidate on other client that has the file cached
        mock_client1.invalidate.assert_called_once_with('a')

    def test_setclients(self):
        """Test setting clients list"""
        s = server(self.mock_files, False, 0)
        mock_clients = [Mock(), Mock()]

        s.setclients(mock_clients)
        self.assertEqual(s.clients, mock_clients)
        self.assertEqual(len(s.cache), 2)

    def test_stats(self):
        """Test server statistics"""
        s = server(self.mock_files, False, 0)
        s.getcnt = 5
        s.putcnt = 3

        with patch('builtins.print') as mock_print:
            s.stats()
            mock_print.assert_called_once_with("Server   -- Gets:5 Puts:3")

    def test_filestats_with_solve(self):
        """Test file statistics with solve enabled"""
        s = server(self.mock_files, True, 0)

        with patch('builtins.print') as mock_print:
            s.filestats(True)
            calls = mock_print.call_args_list
            self.assertIn("file:a contains:0", str(calls[0]))
            self.assertIn("file:b contains:1", str(calls[1]))

    def test_filestats_without_solve(self):
        """Test file statistics with solve disabled"""
        s = server(self.mock_files, False, 0)

        with patch('builtins.print') as mock_print:
            s.filestats(False)
            calls = mock_print.call_args_list
            # Check that print was called with the expected strings
            expected_calls = [
                (("file:a contains:?",), {}),
                (("file:b contains:?",), {})
            ]
            self.assertEqual(len(calls), 2)
            for expected in expected_calls:
                self.assertIn(expected, calls)
