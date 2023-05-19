import unittest
import inspect
from random import choices
import string
from time import sleep, time
from util.file_cache import FileCache


def random_b36(n_chars):
    """ Generate random base 36 string 'n_chars' characters long, """
    return ''.join(choices(string.digits + string.ascii_uppercase, k=n_chars))


class FileCacheTest(unittest.TestCase):

    def test_file_cache(self):
        print('-- %s --' % inspect.stack()[0][3])

        # Open file cahce and make sure it is clean.
        count = 1000
        base_dir = 'test_cache'
        fc = FileCache(base_dir)
        fc.clean(0)

        # Add content to the cache.
        st = time()
        keys = {}
        for _ in range(count):
            key = random_b36(32)
            rec = {k: random_b36(100) for k in string.ascii_lowercase}
            fc.add(key, rec)
            keys[key] = rec
            sleep(.0025)

        # Make sure all content keys are found.
        for key in keys:
            rec = fc.get(key)
            self.assertTrue(rec is not None, 'Expected content to exist.')
            self.assertTrue(rec == keys[key], 'Expected content to be the same.')

        clean_n = fc.clean()
        self.assertTrue(clean_n == 0, 'Expected no cleanup')

        # Open file cache with a lower expiration.
        fc = FileCache(base_dir, expire_secs=(time()-st)/2)
        clean_n = fc.clean()
        self.assertTrue(clean_n > 0, 'Expected files to be cleaned up.')

        # Count remaining files.
        fc = FileCache(base_dir)
        found_n = 0
        for key in keys:
            rec = fc.get(key)
            if rec is not None:
                found_n += 1
        self.assertEqual(count, found_n + clean_n,
                         'Expected remaining content to be found.')


if __name__ == '__main__':
    unittest.main()
