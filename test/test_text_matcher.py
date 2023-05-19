import unittest
import inspect
from util.text_matcher import TextMatcher
from util.timer import Timer


class TextMatcherTest(unittest.TestCase):

    def test_default_matching(self):
        print(inspect.stack()[0][3])
        tx = TextMatcher()
        for w1, w2, es in (('trythis', 'thythis', 0.85714),
                           ('OneOverMany', 'OneOverManyMore', 0.6923),
                           ('classification', 'classify', 0.3636),
                           ('classify', 'chassify', 0.875)):
            sc = tx.match(w1, w2)
            self.assertAlmostEqual(es, sc, 3)

    def test_base_ref_matching(self):
        print(inspect.stack()[0][3])
        tx = TextMatcher(match_type=TextMatcher.MatchType.BASE_REF)
        for w1, w2, es in (('trythis', 'thythis', 0.85714),
                           ('OneOverMany', 'OneOverManyMore', 0.7333),
                           ('classification', 'classify', 0.125),
                           ('classify', 'chassify', 0.875),
                           ('Dusk—of a summer night', 'summer night', 0.3636)):
            sc = tx.match(w1, w2)
            self.assertAlmostEqual(es, sc, 3)

    def test_source_ref_matching(self):
        print(inspect.stack()[0][3])
        tx = TextMatcher(match_type=TextMatcher.MatchType.SOURCE_REF)
        for w1, w2, es in (('trythis', 'thythis', 0.85714),
                           ('OneOverMany', 'OneOverManyMore', 0.6363),
                           ('classification', 'classify', 0.5),
                           ('classify', 'chassify', 0.875),
                           ('Dusk—of a summer night', 'summer night', 0.6111)):
            sc = tx.match(w1, w2)
            self.assertAlmostEqual(es, sc, 3)

    def test_case_sensitivity(self):
        print(inspect.stack()[0][3])
        score = TextMatcher(case_sensitive=False).match('November', 'november')
        self.assertAlmostEqual(1.0, score, 3)
        score = TextMatcher(case_sensitive=True).match('November', 'november')
        self.assertAlmostEqual(0.875, score, 3)

    def test_word_length(self):
        print(inspect.stack()[0][3])
        score = TextMatcher(min_size=2).match('at', 'ate')
        self.assertAlmostEqual(.6, score, 3)
        score = TextMatcher(min_size=3).match('at', 'ate')
        self.assertAlmostEqual(0, score, 3)

    def test_words_special(self):
        print(inspect.stack()[0][3])
        tx = TextMatcher()
        for w1, w2, es in (('for - this - one', 'for/this/one', 1.0),
                           (' blanks ', 'blanks', 1.0),
                           ('/4/5/six.com', '/5/4/six.com', 0.75)):
            sc = tx.match(w1, w2)
            self.assertAlmostEqual(es, sc, 3)

    def test_many_words(self):
        print(inspect.stack()[0][3])
        words = """
        Call me Ishmael. Some years ago — never mind how long
        precisely — having little or no money in my purse, and nothing
        particular to interest me on shore, I thought I would sail about a
        little and see the watery part of the world. It is a way I have of
        driving off the spleen, and regulating the circulation. Whenever
        I find myself growing grim about the mouth; whenever it is a damp,
        drizzly November in my soul; whenever I find myself involuntarily
        pausing before coffin warehouses, and bringing up the rear of every
        funeral I meet; and especially whenever my hypos get such an upper
        hand of me, that it requires a strong moral principle to prevent me
        from deliberately stepping into the street, and methodically knocking
        people’s hats off — then, I account it high time to get to sea as
        soon as I can. This is my substitute for pistol and ball. With a
        philosophical flourish Cato throws himself upon his sword; I quietly
        take to the ship. There is nothing surprising in this. If they but
        knew it, almost all men in their degree, some time or other, cherish
        very nearly the same feelings towards the ocean with me.""".split()
        results = []
        scores = []
        tx = TextMatcher()
        with Timer() as tm:
            for i in range(len(words)):
                for j in range(i, len(words)):
                    w1 = words[i]
                    w2 = words[j]
                    if w1 != w2:
                        sc = tx.match(w1, w2)
                        if sc > 0:
                            results.append((w1, w2, sc))
                            scores.append(sc)
        print(tx, tm)
        self.assertAlmostEqual(0.04, min(scores), 3)
        self.assertAlmostEqual(0.2243, sum(scores) / len(scores), 3)
        self.assertAlmostEqual(1.0, max(scores), 3)


if __name__ == '__main__':
    unittest.main()
