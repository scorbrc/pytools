
import datetime as dt
import unittest
import inspect
import string
from util.random_utils import (
    int_to_b62,
    random_address,
    random_b36,
    random_b62,
    random_comp,
    random_date,
    random_words
)
from util.time_utils import to_utc


class RandomUtilsTest(unittest.TestCase):

    def test_int_to_b62(self):
        print(inspect.stack()[0][3])
        self.assertEqual('HcutVS', int_to_b62(39578292712))

    def test_random_address(self):
        print(inspect.stack()[0][3])
        for _ in range(10):
            addr = random_address()
            self.assertTrue(addr.split()[0].isdigit())
            self.assertTrue(addr.split()[-1].isdigit())

    def test_random_b36(self):
        print(inspect.stack()[0][3])
        rx = random_b36(10)
        self.assertEqual(10, len(rx))
        for c in rx:
            self.assertTrue(
                c in string.digits + string.ascii_uppercase)

    def test_random_b36_chars(self):
        print(inspect.stack()[0][3])
        chrs = set()
        for ch in random_b36(36**2):
            chrs.add(ch)
        self.assertEqual(36, len(chrs))

    def test_random_b62(self):
        print(inspect.stack()[0][3])
        rx = random_b62(10)
        self.assertEqual(10, len(rx))
        for c in rx:
            self.assertTrue(
                c in string.digits +
                string.ascii_lowercase +
                string.ascii_uppercase)

    def test_random_b62_chars(self):
        print(inspect.stack()[0][3])
        chrs = set()
        for ch in random_b62(62**2):
            chrs.add(ch)
        self.assertEqual(62, len(chrs))

    def test_random_comp(self):
        print(inspect.stack()[0][3])
        for n in range(8, 15):
            for _ in range(100):
                try:
                    rc = random_comp(n)
                    self.assertEqual(n, len(rc))
                    self.assertTrue(
                        len([c for c in rc if c in string.ascii_lowercase]) > 0)
                    self.assertTrue(
                        len([c for c in rc if c in string.ascii_uppercase]) > 0)
                    self.assertTrue(len([c for c in rc if c in string.digits]) > 0)
                    self.assertTrue(
                        len([c for c in rc
                             if not c.isdigit() and not c.isalpha()]) > 0)
                except Exception as ex:
                    self.assertFalse(False, "Raised %s" % ex)

    def test_random_date(self):
        print(inspect.stack()[0][3])
        d1 = random_date()
        self.assertTrue(
            d1 > to_utc() - dt.timedelta(seconds=60*60*24*7))
        self.assertTrue(d1 <= to_utc())

    def test_random_words(self):
        print(inspect.stack()[0][3])
        rw = random_words(3)
        self.assertTrue('_' not in rw)
        self.assertEqual(0, len([c for c in rw if c.isupper()]))
        rw = random_words(3, camel=True)
        self.assertEqual(2, len([c for c in rw if c.isupper()]))
        rw = random_words(3, delim='_')
        self.assertEqual(2, len([c for c in rw if c == '_']))

    def test_random_words_camel(self):
        print(inspect.stack()[0][3])
        for _ in range(100):
            word = random_words(3, camel=True)
            self.assertEqual(1, len(word.split()), word)
            self.assertTrue(len([c for c in word if c.isupper()]))

    def test_random_words_snake(self):
        print(inspect.stack()[0][3])
        for _ in range(100):
            word = random_words(3, delim='_')
            self.assertEqual(3, len(word.split('_')), word)
            self.assertTrue(word.islower())

    def test_random_words_spaces(self):
        print(inspect.stack()[0][3])
        for _ in range(100):
            word = random_words(3, delim=' ')
            self.assertEqual(3, len(word.split()), word)
            self.assertTrue(word.islower())


if __name__ == '__main__':
    unittest.main()
