import unittest
from unittest.mock import Mock, patch, call
from afs import client, MICRO_OPEN, MICRO_READ, MICRO_WRITE, MICRO_CLOSE


class TestClient(unittest.TestCase):
    """Test cases for the client class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_server = Mock()
        self.mock_files = Mock()
        self.mock_files.getfiles.return_value = ['a', 'b']

    def test_init_client_with_random_actions(self):
        """Test client initialization with random actions"""
        with patch('afs.random.random', return_value=0.3), \
             patch('afs.pickrand', return_value='a'):
            c = client("c0", 0, self.mock_server, self.mock_files,
                      [0.5, 1.0], 2, "", False, 0)

        self.assertEqual(c.name, "c0")
        self.assertEqual(c.cid, 0)
        self.assertEqual(c.server, self.mock_server)
        self.assertEqual(c.files, self.mock_files)
        self.assertEqual(len(c.acts), 6)  # 2 operations * 3 actions each

    def test_init_client_with_specific_actions(self):
        """Test client initialization with specific actions"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1:r1:c1", False, 0)

        self.assertEqual(len(c.acts), 3)
        self.assertEqual(c.acts[0], (MICRO_OPEN, 'a', 1))
        self.assertEqual(c.acts[1], (MICRO_READ, 1))
        self.assertEqual(c.acts[2], (MICRO_CLOSE, 1))

    def test_init_client_malformed_open_action(self):
        """Test client initialization with malformed open action"""
        # This should not raise an exception because "oa1" is actually valid
        # (open file 'a' with descriptor 1)
        try:
            c = client("c0", 0, self.mock_server, self.mock_files,
                      [], 0, "oa1", False, 0)
            # If we get here, the action was parsed successfully
            self.assertEqual(len(c.acts), 1)
        except SystemExit:
            self.fail("Unexpected SystemExit for valid action 'oa1'")

    def test_init_client_malformed_read_action(self):
        """Test client initialization with malformed read action"""
        with self.assertRaises(SystemExit):
            client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1:r:c1", False, 0)

    def test_init_client_unrecognized_action(self):
        """Test client initialization with unrecognized action"""
        with self.assertRaises(SystemExit):
            client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1:x1:c1", False, 0)

    def test_getname(self):
        """Test getname method"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [0.5, 1.0], 1, "", False, 0)
        self.assertEqual(c.getname(), "c0")

    @patch('afs.pickrand')
    def test_getfile_cache_hit(self, mock_pickrand):
        """Test getfile when file is in cache and valid"""
        mock_pickrand.return_value = 'a'
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [0.5, 1.0], 1, "", False, 0)

        # Mock cache to return hit
        with patch.object(c.cache, 'checkget', return_value=(True, {"valid": True})) as mock_checkget:
            with patch.object(c.cache, 'put') as mock_put:
                with patch.object(c.cache, 'incref') as mock_incref:
                    c.getfile("a")

                    mock_checkget.assert_called_once_with("a")
                    mock_put.assert_not_called()
                    mock_incref.assert_called_once_with("a")
                    self.mock_server.get.assert_not_called()

    @patch('afs.pickrand')
    def test_getfile_cache_miss(self, mock_pickrand):
        """Test getfile when file is not in cache"""
        mock_pickrand.return_value = 'a'
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [0.5, 1.0], 1, "", False, 0)

        # Mock cache to return miss
        with patch.object(c.cache, 'checkget', return_value=(False, -1)) as mock_checkget:
            with patch.object(c.cache, 'put') as mock_put:
                with patch.object(c.cache, 'incref') as mock_incref:
                    self.mock_server.get.return_value = 42

                    c.getfile("a")

                    mock_checkget.assert_called_once_with("a")
                    self.mock_server.get.assert_called_once_with("c0", "a")
                    mock_put.assert_called_once_with("a", 42, False, 0)
                    mock_incref.assert_called_once_with("a")

    def test_putfile(self):
        """Test putfile operation"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [0.5, 1.0], 1, "", False, 0)

        # Need to put file in cache first
        c.cache.put("a", 42, False, 1)

        with patch.object(c.cache, 'setclean') as mock_setclean:
            with patch.object(c.cache, 'setvalid') as mock_setvalid:
                c.putfile("a", 100)

                c.server.put.assert_called_once_with("c0", "a", 100)
                mock_setclean.assert_called_once_with("a")
                mock_setvalid.assert_called_once_with("a")

    def test_invalidate(self):
        """Test invalidate operation"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [0.5, 1.0], 1, "", False, 0)

        with patch.object(c.cache, 'invalidate') as mock_invalidate:
            c.invalidate("a")
            mock_invalidate.assert_called_once_with("a")

    def test_step_open_action(self):
        """Test step method with open action"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1", False, 0)

        with patch('afs.dospace'), \
             patch('afs.tprint') as mock_tprint, \
             patch.object(c, 'getfile') as mock_getfile:

            result = c.step(0)

            mock_tprint.assert_called_once_with("open:a [fd:1]")
            mock_getfile.assert_called_once_with("a")
            self.assertEqual(result, 1)
            self.assertEqual(c.acnt, 1)

    def test_step_read_action_solve_enabled(self):
        """Test step method with read action when solve is enabled"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1:r1", True, 0)

        # Mock file descriptor allocation
        with patch.object(c.fd, 'alloc', return_value=1):
            with patch.object(c.cache, 'get', return_value=(True, {"data": 42})):
                with patch('afs.dospace'), \
                     patch('afs.tprint') as mock_tprint:

                    c.step(0)  # Process open first
                    c.step(0)  # Process read

                    mock_tprint.assert_any_call("read:1 -> 42")

    def test_step_read_action_solve_disabled(self):
        """Test step method with read action when solve is disabled"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1:r1", False, 0)

        # Mock file descriptor allocation
        with patch.object(c.fd, 'alloc', return_value=1):
            with patch.object(c.cache, 'get', return_value=(True, {"data": 42})):
                with patch('afs.dospace'), \
                     patch('afs.tprint') as mock_tprint:

                    c.step(0)  # Process open first
                    c.step(0)  # Process read

                    mock_tprint.assert_any_call("read:1 -> value?")

    def test_step_write_action_solve_enabled(self):
        """Test step method with write action when solve is enabled"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1:w1", True, 0)

        # Mock file descriptor allocation and file value generation
        with patch.object(c.fd, 'alloc', return_value=1):
            with patch.object(c.cache, 'get', return_value=(True, {"data": 42})):
                with patch.object(c.files, 'getvalue', return_value=100):
                    with patch.object(c.cache, 'update') as mock_update:
                        with patch('afs.dospace'), \
                             patch('afs.tprint') as mock_tprint:

                            c.step(0)  # Process open first
                            c.step(0)  # Process write

                            mock_tprint.assert_any_call("write:1 42 -> 100")
                            mock_update.assert_called_once_with("a", 100)

    def test_step_close_action_dirty_file(self):
        """Test step method with close action on dirty file"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1:c1", False, 0)

        # Mock file descriptor allocation
        with patch.object(c.fd, 'alloc', return_value=1):
            with patch.object(c.cache, 'get', return_value=(True, {"data": 42})):
                with patch.object(c.cache, 'isdirty', return_value=True):
                    with patch.object(c, 'putfile') as mock_putfile:
                        with patch.object(c.cache, 'decref') as mock_decref:
                            with patch.object(c.cache, 'checkvalid') as mock_checkvalid:
                                with patch('afs.dospace'), \
                                     patch('afs.tprint') as mock_tprint:

                                    c.step(0)  # Process open first
                                    c.step(0)  # Process close

                                    mock_tprint.assert_any_call("close:1")
                                    mock_putfile.assert_called_once_with("a", 42)
                                    mock_decref.assert_called_once_with("a")
                                    mock_checkvalid.assert_called_once_with("a")

    def test_step_close_action_clean_file(self):
        """Test step method with close action on clean file"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1:c1", False, 0)

        # Mock file descriptor allocation
        with patch.object(c.fd, 'alloc', return_value=1):
            with patch.object(c.cache, 'get', return_value=(True, {"data": 42})):
                with patch.object(c.cache, 'isdirty', return_value=False):
                    with patch.object(c, 'putfile') as mock_putfile:
                        with patch.object(c.cache, 'decref') as mock_decref:
                            with patch.object(c.cache, 'checkvalid') as mock_checkvalid:
                                with patch('afs.dospace'), \
                                     patch('afs.tprint') as mock_tprint:

                                    c.step(0)  # Process open first
                                    c.step(0)  # Process close

                                    mock_tprint.assert_any_call("close:1")
                                    mock_putfile.assert_not_called()
                                    mock_decref.assert_called_once_with("a")
                                    mock_checkvalid.assert_called_once_with("a")

    def test_step_completed_client(self):
        """Test step method when client has completed all actions"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [], 0, "oa1", False, 0)

        c.done = True
        result = c.step(0)
        self.assertEqual(result, -1)

    def test_stats(self):
        """Test client statistics"""
        c = client("c0", 0, self.mock_server, self.mock_files,
                  [0.5, 1.0], 1, "", False, 0)

        c.readcnt = 3
        c.writecnt = 2

        with patch('builtins.print') as mock_print:
            c.stats()

            # Verify stats print calls
            calls = mock_print.call_args_list
            self.assertIn("c0", str(calls[0]))
            self.assertIn("Reads:3", str(calls[0]))
            self.assertIn("Writes:2", str(calls[0]))
