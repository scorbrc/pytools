import unittest
import inspect
from util.short_uid import ShortUID
from util.timer import Timer


class ShortUIDTest(unittest.TestCase):

    def test_short_uid_length(self):
        print(inspect.stack()[0][3])
        short_uid = ShortUID()
        for _ in range(100000):
            uid = short_uid.next()
            self.assertEqual(12, len(uid))

    def test_short_uid_series(self):
        print(inspect.stack()[0][3])
        short_uid = ShortUID()
        self.assertTrue(short_uid.next().startswith('x'))
        short_uid = ShortUID('a')
        self.assertTrue(short_uid.next().startswith('a'))
        with self.assertRaises(ValueError):
            ShortUID('ab')

    def test_short_uid_collision(self):
        print(inspect.stack()[0][3])
        uids = set()
        short_uid = ShortUID()
        count = 1000000
        with Timer() as tm:
            for _ in range(count):
                uids.add(short_uid.next())
        self.assertEqual(count, len(uids))
        self.assertTrue(tm.secs < 2)


if __name__ == '__main__':
    unittest.main()
