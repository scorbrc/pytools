import datetime as dt
import unittest
import string
from util.random_utils import RandomUtils
from util.timer import Timer
from util.time_utils import to_utc
from util.util_tools import get_source_info


class RandomUtilsTest(unittest.TestCase):

    def test_int_to_b62(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        self.assertEqual('HcutVS', ru.int_to_b62(39578292712))

    def test_random_address(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for _ in range(10):
            addr = ru.street_address()
            self.assertTrue(addr[0].partition(' ')[0].isdigit())
            self.assertTrue(addr[-1].isdigit())

    def test_base_random_chars(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for name in ('b16', 'b36', 'b62', 'b74'):
            func = getattr(ru, name)
            for n in range(1, 16):
                rx = func(n)
                self.assertEqual(n, len(rx))

    def test_base_random_chars_many(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for name in ('b16', 'b36', 'b62', 'b74'):
            chars = set()
            func = getattr(ru, name)
            for _ in range(10000):
                for ch in func(20):
                    chars.add(ch)
            exp_n = int(name[1:])
            self.assertEqual(exp_n, len(chars),
                             "Expected %s to have %d unique digits." %
                             (func.__name__, exp_n))

    def test_comp_chars(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for n in range(8, 15):
            for _ in range(100):
                try:
                    rc = ru.comp_chars(n)
                    self.assertEqual(n, len(rc))
                    self.assertTrue(
                        len([c for c in rc if c in string.ascii_lowercase]) > 0)
                    self.assertTrue(
                        len([c for c in rc if c in string.ascii_uppercase]) > 0)
                    self.assertTrue(
                        len([c for c in rc if c in string.digits]) > 0)
                    self.assertTrue(
                        len([c for c in rc
                             if not c.isdigit() and not c.isalpha()]) > 0)
                except Exception as ex:
                    self.assertFalse(False, "Raised %s" % ex)

    def test_comp_words(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for n in range(12, 37):
            for _ in range(10):
                x = ru.comp_words(n)
                self.assertEqual(n, len(x))

    def test_date(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        d1 = ru.date()
        self.assertTrue(
            d1 > to_utc() - dt.timedelta(seconds=60 * 60 * 24 * 30))
        self.assertTrue(d1 <= to_utc())

    def test_email_address(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        email = ru.email_address()
        self.assertTrue(len(email))
        self.assertTrue('@' in email)
        pname = ru.personal_name()
        email = ru.email_address(pname)
        self.assertTrue(pname[0] in email)
        cname = ru.company_name()
        email = ru.email_address(cname=cname)
        self.assertTrue(cname.lower() in email,
                        "Expected %s in %s" % (cname.lower(), email))

    def test_phone(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        phone = ru.phone()
        self.assertEqual(13, len(phone))
        self.assertTrue(
            phone.replace('(', '').replace(')', '').replace('-', '').isdigit())

    def test_seeding(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru1 = RandomUtils(2784673)
        ru2 = RandomUtils(2784673)
        ru3 = RandomUtils(4845720)
        uid1 = ru1.b16(32)
        uid2 = ru2.b16(32)
        uid3 = ru3.b16(32)
        self.assertEqual(uid1, uid2)
        self.assertNotEqual(uid1, uid3)

    def test_short_uid(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for _ in range(10):
            uid = ru.short_uid()
            self.assertEqual(12, len(uid), uid)
            for ch in uid:
                self.assertTrue(ch in RandomUtils.B62_CHARS)

    def test_short_uid_unique(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        uids = set()
        count = 100000
        for _ in range(count):
            uids.add(ru.short_uid())
        self.assertEqual(count, len(uids))

    def test_words(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        rw = ru.words(3)
        self.assertTrue('_' not in rw)
        self.assertEqual(0, len([c for c in rw if c.isupper()]))

    def test_join(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        rw = ru.join(ru.words(3), camel=True)
        self.assertEqual(2, len([c for c in rw if c.isupper()]))
        rw = ru.join(ru.words(3), delim='_')
        self.assertEqual(2, len([c for c in rw if c == '_']))

    def test_random_words_camel(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for _ in range(100):
            word = ru.join(ru.words(3), camel=True)
            self.assertEqual(1, len(word.split()), word)
            self.assertTrue(len([c for c in word if c.isupper()]))

    def test_random_words_snake(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for _ in range(100):
            word = ru.join(ru.words(3), delim='_')
            self.assertEqual(3, len(word.split('_')), word)
            self.assertTrue(word.islower(), word)

    def test_random_words_spaces(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        for _ in range(100):
            word = ru.join(ru.words(3), delim=' ')
            self.assertEqual(3, len(word.split()), word)
            self.assertTrue(word.islower(), word)


if __name__ == '__main__':
    unittest.main()
