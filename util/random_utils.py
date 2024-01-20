""" Random utility tools. """
import datetime as dt
from math import ceil
from random import Random
from string import digits, ascii_lowercase, ascii_uppercase
from time import time
from util.time_utils import to_utc
from util.words import words


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

    def __init__(self, seed=None):
        """
        Create a RandomUtils with it's own random generator seeded by 'seed',
        default current epoch time.
        """
        self.__words = []
        self.__rnd = Random(seed)
        self.__short_uid_seq = 0

    def b16(self, n_chars=10):
        """ Generate random base 16 string 'n_chars' characters long, """
        return ''.join([self.__rnd.choice(RandomUtils.B16_CHARS)
                       for _ in range(n_chars)])

    def b36(self, n_chars=10):
        """ Generate random base 36 string 'n_chars' characters long, """
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
            if n >= 2 and n <= 4:
                rx = self.comp_chars(n, (digits, RandomUtils.PUNCT))
                ws += [*rx]
                self.__rnd.shuffle(ws)
                return ''.join(ws)
        raise ValueError("Failed to build comp_words.")

    def count(self, minv, midv, maxv, shape):
        """
        Generate a random integer no lower than 'minv', a midpoint
        around 'midv' and no higher than 'maxv' and having 'shape'
        (.25 <= shape <= 4) which will control the skew. Lower the value
        the greater the skew, shape=1 is approximately exponential.
        """
        rn = self.__rnd.weibullvariate(midv, shape) * shape
        return ceil(min(max(rn, minv), maxv))

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

    def random(self):
        return self.__rnd

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

    def words(self, count=1):
        """ Generate 'count' random words. """
        wds = self.__rnd.sample(words, k=count)
        if count == 1:
            return wds[0]
        return wds


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "type",
        action="store",
        choices=(('chars', 'words')),
        default='chars',
        help="Type of random string to generate."
    )
    parser.add_argument(
        "--size",
        action='store',
        type=int,
        default=10,
        help="Size of random string to generate."
    )
    parser.add_argument(
        "--count",
        action='store',
        type=int,
        default=10,
        help="Number of random strings to generate."
    )
    args = parser.parse_args()

    ru = RandomUtils()
    for _ in range(args.count):
        if args.type == 'chars':
            print(ru.comp_chars(args.size))
        else:
            print(ru.comp_words(args.size))
