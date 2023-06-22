import unittest
from util.describer import describe
from util.levenshtein import levenshtein
from util.random_utils import RandomUtils
from util.timer import Timer
from util.util_tools import get_source_info


class LevenshteinTest(unittest.TestCase):

    def test_levenshtein_chars(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(1.0, levenshtein('abcdefgh', 'abcdefgh'), 3)
        self.assertAlmostEqual(.875, levenshtein('abcdefgh', 'abzdefgh'), 3)
        self.assertAlmostEqual(.75, levenshtein('abcdefgh', 'abzzefgh'), 3)
        self.assertAlmostEqual(.875, levenshtein('abcdefgh', 'abcdefg'), 3)
        self.assertAlmostEqual(.75, levenshtein('abcdefgh', 'bcdefg'), 3)
        self.assertAlmostEqual(.75, levenshtein('abcdefgh', 'abfdecgh'), 3)

    def test_levenshtein_words(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(1.0, levenshtein('levenshtein', 'levenshtein'), 3)
        self.assertAlmostEqual(.909, levenshtein('levenshtein', 'levenstein'), 3)
        self.assertAlmostEqual(.727, levenshtein('levenshtein', 'levenstien'), 3)

    def test_levenshtein_many(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        scores = []
        k = 1000
        n = 10
        with Timer() as tm:
            for _ in range(k):
                for w1, w2 in zip(ru.words(n, 'other'), ru.words(10, 'other')):
                    scores.append(levenshtein(w1, w2))
        ds = describe(scores)
        self.assertEqual(k*n, ds.n, ds)
        self.assertTrue(ds.p50 > .12, ds)
        self.assertTrue(tm.secs < .2, tm)


if __name__ == '__main__':
    unittest.main()
