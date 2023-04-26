import unittest
from os.path import join, dirname
from pathlib import Path
import shutil

import caching


class TestCache(unittest.TestCase):
    tmp_folder = Path(join(dirname(__file__), 'tmp'))
    cache_file = join(tmp_folder, 'test.dat')

    def setUp(self) -> None:
        self.tmp_folder.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_folder)

    def test_make_cache(self):
        cache1 = caching.make_cache(self.cache_file, n=5)
        cache2 = caching.make_cache(self.cache_file)
        self.assertEqual(cache1.n, cache2.n)
        self.assertEqual(cache1.n, 5)

    def test_update_n(self):
        cache = caching.make_cache(self.cache_file)
        cache.n = 10
        cache.save()
        cache1 = caching.make_cache(self.cache_file)
        self.assertEqual(cache.n, cache1.n)
        self.assertEqual(cache1.n, 10)

    def test_caching(self):
        cache = caching.make_cache(self.cache_file)
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3
        self.assertIn('a', cache)
        self.assertIn('b', cache)
        self.assertIn('c', cache)
        self.assertNotIn('d', cache)

    def test_eviction(self):
        cache = caching.make_cache(self.cache_file, n=3)
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3
        cache['d'] = 4
        self.assertNotIn('a', cache)
        self.assertIn('b', cache)
        self.assertIn('c', cache)
        self.assertIn('d', cache)

    def test_MRU(self):
        cache = caching.make_cache(self.cache_file, n=3)
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        # Querying the value here should make it last to be evicted
        self.assertEqual(cache['a'], 1)

        cache['d'] = 4
        self.assertNotIn('b', cache)
        self.assertIn('c', cache)
        self.assertIn('a', cache)
        self.assertIn('d', cache)

        cache['e'] = 5
        self.assertNotIn('c', cache)
        self.assertIn('a', cache)
        self.assertIn('d', cache)
        self.assertIn('e', cache)

        cache['f'] = 6
        self.assertNotIn('a', cache)
        self.assertIn('d', cache)
        self.assertIn('e', cache)
        self.assertIn('f', cache)

    def test_no_MRU(self):
        cache = caching.make_cache(self.cache_file, n=3, mru=False)
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        # Querying the value here would normally make it last to be evicted, but MRU is off
        self.assertEqual(cache['a'], 1)

        cache['d'] = 4
        self.assertNotIn('a', cache)
        self.assertIn('b', cache)
        self.assertIn('c', cache)
        self.assertIn('d', cache)

        cache['e'] = 5
        self.assertNotIn('b', cache)
        self.assertIn('c', cache)
        self.assertIn('d', cache)
        self.assertIn('e', cache)

        cache['f'] = 6
        self.assertNotIn('c', cache)
        self.assertIn('d', cache)
        self.assertIn('e', cache)
        self.assertIn('f', cache)

    def test_persist(self):
        cache = caching.make_cache(self.cache_file, n=3, mru=False)
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3
        self.assertEqual(cache['a'], 1)
        cache.save()

        cache1 = caching.make_cache(self.cache_file)
        self.assertIn('a', cache1)
        self.assertIn('b', cache1)
        self.assertIn('c', cache1)

        cache1['d'] = 4
        self.assertNotIn('a', cache1)
        self.assertIn('b', cache1)
        self.assertIn('c', cache1)
        self.assertIn('d', cache1)

        # Verify only the new cache was updated
        self.assertIn('a', cache)
        self.assertIn('b', cache)
        self.assertIn('c', cache)
        self.assertNotIn('d', cache)


if __name__ == '__main__':
    unittest.main()
