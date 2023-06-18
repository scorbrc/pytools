""" Random utility tools. """
import datetime as dt
import json
from random import Random
from string import digits, ascii_lowercase, ascii_uppercase
from time import time
from util.time_utils import to_utc
from util.words import Words


class RandomUtils:
    """
    Utilities for generating random characters, worsds and fields.
    """
    PUNCT = '!#$%&*+=?@~^'
    B16_CHARS = '0123456789ABCDEF'
    B36_CHARS = digits + ascii_uppercase
    B62_CHARS = digits + ascii_lowercase + ascii_uppercase
    B74_CHARS = B62_CHARS + PUNCT
    CHAR_TYPES = (digits, ascii_uppercase, ascii_lowercase, PUNCT)

    def __init__(self, seed=None, fp="words/words_db.js"):
        """
        Create a RandomUtils with it's own random generator seeded by 'seed',
        default current epoch time.
        """
        self.__words = Words()
        self.__rnd = Random(seed)
        self.__short_uid_seq = 0

    def b16(self, n_chars=10):
        """ Generate random base 16 string 'n_chars' characters long, """
        return ''.join([self.__rnd.choice(RandomUtils.B16_CHARS)
                       for _ in range(n_chars)])

    def b36(self, n_chars=10):
        """ Generate random base 62 string 'n_chars' characters long, """
        return ''.join(self.__rnd.choices(RandomUtils.B36_CHARS, k=n_chars))

    def b62(self, n_chars=10):
        """ Generate random base 62 string 'n_chars' characters long, """
        return ''.join(self.__rnd.choices(RandomUtils.B62_CHARS, k=n_chars))

    def b74(self, n_chars=10):
        """ Generate random base 74 string 'n_chars' characters long, """
        return ''.join(self.__rnd.choices(RandomUtils.B74_CHARS, k=n_chars))

    def comp_chars(self, n_chars=10, char_types=None):
        """
        Generate a random composite string 'n_chars' long composed with at least
        one each of 'char_types', which defaults to lower case, one upper case,
        one digit, and one special character. Example: nEfZ*rPk2=
        """
        if char_types is None:
            char_types = RandomUtils.CHAR_TYPES
        rn = [self.__rnd.choice(ch) for ch in char_types]
        for _ in range(n_chars - len(char_types)):
            rn.append(self.__rnd.choice(self.__rnd.choice(char_types)))
        self.__rnd.shuffle(rn)
        return ''.join(rn)

    def comp_words(self, n_chars=16, attempts=200):
        """
        Generate composite words 'n_chars' long (12 <= n_chars <= 36) as a
        combination of capitalized words and digits and punctuation characters.
        """
        n_chars = min(max(n_chars, 12), 36)
        words_n = n_chars // 6
        for i in range(attempts):
            ws = [w.capitalize() for w in self.words(words_n)]
            n = n_chars - sum([len(w) for w in ws])
            if n >= 2 and n <= 5:
                rx = self.comp_chars(n, (digits, RandomUtils.PUNCT))
                return ''.join(self.__rnd.sample(ws + [rx], k=len(ws) + 1))
        raise ValueError("Failed to build comp_words.")

    def company_name(self):
        """ Generate two word string as a company name. """
        return self.join(self.words(2, "places"), camel=True)

    def date(self, min_date=None, max_date=None):
        """
        Generate a random data relative to 'latest_date' if given, defaults to
        current date/time, and up to 'max_offset_secs' before 'latest_date'.
        """
        if max_date is None:
            max_date = to_utc()
        if min_date is None:
            min_date = max_date - dt.timedelta(seconds=30 * 24 * 60 * 60)
        secs = self.__rnd.randint(
            1, int((max_date - min_date).total_seconds()))
        return to_utc() - dt.timedelta(seconds=secs)

    def digits(self, n_chars=10):
        """ Generate 'n_chars' of random digits. """
        return ''.join([self.__rnd.choice(digits) for _ in range(n_chars)])

    def email_address(self, pname=None, cname=None):
        """
        Generate an email address using personal name 'pname' and company
        name 'cname' as firt.middle.last@company,com.
        """
        if pname is None:
            pname = self.personal_name()
        if cname is None:
            cname = self.company_name()
        email = '.'.join([n for n in pname if len(n)])
        domain = "%s.com" % cname.lower()
        return "%s@%s" % (email, domain)

    @staticmethod
    def int_to_b62(num):
        """ Convert integer num to base 62 string. """
        bnum = RandomUtils.B62_CHARS[num % 62]
        while num >= 62:
            num //= 62
            bnum = RandomUtils.B62_CHARS[num % 62] + bnum
        return bnum

    @staticmethod
    def join(wds, camel=False, delim=''):
        """
        Join list of words 'wds' as camel case if 'camel' is True or
        by delimiter 'delim'.
        """
        if camel:
            wds = [w.capitalize() if k > 0 else w for k, w in enumerate(wds)]
        return delim.join(wds)

    def personal_name(self):
        """ Generate personal as (first, middle initial, last). """
        fn = self.words(1, "first_names").capitalize()
        ln = self.words(1, "last_names").capitalize()
        mi = ''
        if self.__rnd.random() < .9:
            mi = self.__rnd.choice(ascii_uppercase)
        return [fn, mi, ln]

    def phone(self):
        """ Generate a random telephone number. """
        return "(%d%02d)%d%02d-%04d" % \
               (self.__rnd.randint(2, 7),
                self.__rnd.randint(0, 99),
                self.__rnd.randint(1, 9),
                self.__rnd.randint(0, 99),
                self.__rnd.randint(0, 9999))

    def short_uid(self):
        """
        Generate a short UID 12 characters long, containing epoch milliseconds,
        a sequence number that recycles after 62**2 allocations, and three
        random characters, all base62.
        """
        ms = int(time() * 1000)
        if self.__short_uid_seq == 62**2:
            self.__short_uid_seq = 0
        self.__short_uid_seq += 1
        sq = RandomUtils.int_to_b62(self.__short_uid_seq)
        if len(sq) < 2:
            sq += self.b62(1)
        chs = "%s%s%s" % ((self.b62(3), self.int_to_b62(ms), sq))
        return ''.join(self.__rnd.sample(chs, k=12))

    def street_address(self):
        """
        Generate a street address as (number and street, city, state, zip).
        """
        rn = self.__rnd.random()
        if rn < .85:
            num = self.__rnd.randint(1, 100)
        elif rn < .98:
            num = self.__rnd.randint(1, 1000)
        else:
            num = self.__rnd.randint(1, 10000)
        street = ' '.join(
            [w.capitalize() for w in self.words(word_type='streets').split()])
        city, state, zip = self.words(word_type='city_state_zips').split('|')
        return ["%d %s" % (num, street),
                city.capitalize(),
                state.upper(),
                zip]

    def words(self, count=1, word_type=None):
        """
        Generate 'count' random words or type 'word_type', formatted in
        camel case if 'camel' is True or with 'delim' as the separator.
        """
        if word_type is None:
            wx = self.__words.get_words()
        else:
            wx = self.__words.get_words(word_type)
        if count >= len(wx):
            raise ValueError("Not enough values in %s." % word_type)
        wds = self.__rnd.sample(wx, k=count)
        if count == 1:
            return wds[0]
        return wds


if __name__ == '__main__':

    import sys

    size = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    ru = RandomUtils()
    for _ in range(count):
        print(ru.comp_chars(size))
