import unittest
from unittest.mock import Mock, patch
from afs import cache


class TestCache(unittest.TestCase):
    """Test cases for the cache class"""

    def setUp(self):
        """Set up test fixtures"""
        self.cache_instance = cache("c0", 0, False, 0)

    def test_init_cache(self):
        """Test cache initialization"""
        self.assertEqual(self.cache_instance.name, "c0")
        self.assertEqual(self.cache_instance.num, 0)
        self.assertFalse(self.cache_instance.solve)
        self.assertEqual(self.cache_instance.detail, 0)
        self.assertEqual(self.cache_instance.cache, {})
        self.assertEqual(self.cache_instance.hitcnt, 0)
        self.assertEqual(self.cache_instance.misscnt, 0)
        self.assertEqual(self.cache_instance.invalidcnt, 0)

    def test_put_file(self):
        """Test putting file in cache"""
        self.cache_instance.put("a", 42, False, 1)

        self.assertIn("a", self.cache_instance.cache)
        entry = self.cache_instance.cache["a"]
        self.assertEqual(entry["data"], 42)
        self.assertFalse(entry["dirty"])
        self.assertEqual(entry["refcnt"], 1)
        self.assertTrue(entry["valid"])

    def test_update_file(self):
        """Test updating file data in cache"""
        self.cache_instance.put("a", 42, False, 1)
        self.cache_instance.update("a", 100)

        entry = self.cache_instance.cache["a"]
        self.assertEqual(entry["data"], 100)
        self.assertTrue(entry["dirty"])
        self.assertEqual(entry["refcnt"], 1)
        self.assertTrue(entry["valid"])

    def test_invalidate_existing_file(self):
        """Test invalidating existing file in cache"""
        self.cache_instance.put("a", 42, False, 1)

        with patch('afs.dospace'), \
             patch.object(self.cache_instance, 'printstate') as mock_printstate:
            self.cache_instance.invalidate("a")

        self.assertEqual(self.cache_instance.invalidcnt, 1)
        entry = self.cache_instance.cache["a"]
        self.assertFalse(entry["valid"])

    def test_invalidate_nonexistent_file(self):
        """Test invalidating file not in cache"""
        # Should not raise exception and should not increment counter
        initial_count = self.cache_instance.invalidcnt
        self.cache_instance.invalidate("nonexistent")
        self.assertEqual(self.cache_instance.invalidcnt, initial_count)

    def test_checkvalid_remove_invalid_file(self):
        """Test checkvalid removes invalid file with zero refcnt"""
        self.cache_instance.put("a", 42, False, 0)
        self.cache_instance.invalidate("a")

        self.cache_instance.checkvalid("a")
        self.assertNotIn("a", self.cache_instance.cache)

    def test_checkvalid_keep_invalid_file_with_refcnt(self):
        """Test checkvalid keeps invalid file with positive refcnt"""
        self.cache_instance.put("a", 42, False, 1)
        self.cache_instance.invalidate("a")

        self.cache_instance.checkvalid("a")
        self.assertIn("a", self.cache_instance.cache)
        self.assertFalse(self.cache_instance.cache["a"]["valid"])

    def test_checkget_cache_hit(self):
        """Test checkget with cache hit"""
        self.cache_instance.put("a", 42, False, 1)

        hit, entry = self.cache_instance.checkget("a")
        self.assertTrue(hit)
        self.assertEqual(entry["data"], 42)
        self.assertEqual(self.cache_instance.hitcnt, 1)
        self.assertEqual(self.cache_instance.misscnt, 0)

    def test_checkget_cache_miss(self):
        """Test checkget with cache miss"""
        hit, entry = self.cache_instance.checkget("a")
        self.assertFalse(hit)
        self.assertEqual(entry, -1)
        self.assertEqual(self.cache_instance.hitcnt, 0)
        self.assertEqual(self.cache_instance.misscnt, 1)

    def test_get_existing_file(self):
        """Test get operation on existing file"""
        self.cache_instance.put("a", 42, False, 1)

        hit, entry = self.cache_instance.get("a")
        self.assertTrue(hit)
        self.assertEqual(entry["data"], 42)

    def test_get_nonexistent_file(self):
        """Test get operation on nonexistent file"""
        with self.assertRaises(AssertionError):
            self.cache_instance.get("nonexistent")

    def test_incref_existing_file(self):
        """Test incrementing reference count"""
        self.cache_instance.put("a", 42, False, 1)
        self.cache_instance.incref("a")

        entry = self.cache_instance.cache["a"]
        self.assertEqual(entry["refcnt"], 2)

    def test_decref_existing_file(self):
        """Test decrementing reference count"""
        self.cache_instance.put("a", 42, False, 2)
        self.cache_instance.decref("a")

        entry = self.cache_instance.cache["a"]
        self.assertEqual(entry["refcnt"], 1)

    def test_setdirty(self):
        """Test setting file as dirty"""
        self.cache_instance.put("a", 42, False, 1)
        self.cache_instance.setdirty("a", True)

        entry = self.cache_instance.cache["a"]
        self.assertTrue(entry["dirty"])

    def test_setclean(self):
        """Test setting file as clean"""
        self.cache_instance.put("a", 42, True, 1)
        self.cache_instance.setclean("a")

        entry = self.cache_instance.cache["a"]
        self.assertFalse(entry["dirty"])

    def test_isdirty_true(self):
        """Test isdirty returns True for dirty file"""
        self.cache_instance.put("a", 42, True, 1)
        self.assertTrue(self.cache_instance.isdirty("a"))

    def test_isdirty_false(self):
        """Test isdirty returns False for clean file"""
        self.cache_instance.put("a", 42, False, 1)
        self.assertFalse(self.cache_instance.isdirty("a"))

    def test_setvalid(self):
        """Test setting file as valid"""
        self.cache_instance.put("a", 42, False, 1)
        self.cache_instance.invalidate("a")
        self.assertFalse(self.cache_instance.cache["a"]["valid"])

        self.cache_instance.setvalid("a")
        self.assertTrue(self.cache_instance.cache["a"]["valid"])

    def test_stats(self):
        """Test cache statistics"""
        self.cache_instance.hitcnt = 5
        self.cache_instance.misscnt = 3
        self.cache_instance.invalidcnt = 2

        with patch('builtins.print') as mock_print:
            self.cache_instance.stats()
            mock_print.assert_called_once_with(
                "   Cache -- Hits:5 Misses:3 Invalidates:2"
            )

    def test_printstate_with_detail(self):
        """Test printstate with detail enabled"""
        self.cache_instance = cache("c0", 0, True, 4)
        self.cache_instance.put("a", 42, True, 2)

        with patch('afs.dospace'), \
             patch('builtins.print') as mock_print:
            self.cache_instance.printstate("c0")
            # Verify that print was called (exact format checking would be complex)
            self.assertTrue(mock_print.called)
