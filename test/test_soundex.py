import unittest
from util.profiler import Profiler
from util.soundex import soundex
from util.random_utils import RandomUtils
from util.timer import Timer
from util.util_tools import get_source_info


class SoundexTest(unittest.TestCase):

    def test_soundex(self):
        print("-- %s(%d): %s --" % get_source_info())
        for word, snd4, snd5 in (('small', 'S540', 'S5400'),
                                 ('large', 'L620', 'L6200'),
                                 ('upper', 'U160', 'U1600'),
                                 ('lower', 'L600', 'L6000'),
                                 ('operate', 'O163', 'O1630'),
                                 ('operations', 'O163', 'O1635')):
            self.assertEqual(snd4, soundex(word, 4))
            self.assertEqual(snd5, soundex(word, 5))

    def test_soundex_non_alpha(self):
        print("-- %s(%d): %s --" % get_source_info())
        for word, snd in (('try/this', 'T632'),
                          ('Or$this', 'O632')):
            self.assertEqual(snd, soundex(word))

    def test_soundex_many_words(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        snds = set()
        size = 5
        k = 10000
        with Timer() as tm:
            with open('/usr/share/dict/words') as fi:
                for _ in range(k):
                    snds.add(soundex(ru.words(1, 'other'), size))
        self.assertTrue(len(snds) > k / 4, len(snds))
        self.assertTrue(tm.secs < .025, tm)


if __name__ == '__main__':
    unittest.main()
