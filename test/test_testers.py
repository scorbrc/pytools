import unittest
import inspect
from random import weibullvariate
from test_evaluator import TestEvaluator
from util.open_record import OpenRecord
from util.testers import (
    cusum,
    ewma,
    pcusum,
    pewma,
    tcusum,
    tewma
)

DATA1 = [0.12, 0.13, 0.13, 0.14, 0.15, 0.16, 0.2, 0.23, 0.33, 0.45, 0.53,
         0.66, 0.79, 0.9, 0.98, 1.16, 1.65, 1.72, 1.87, 2.01, 2.26, 2.34,
         2.42, 3.92, 5.29, 5.93, 6.5, 11.34, 11.76, 14.66, 16.25, 23.86,
         27.64, 71.82, 79.04]


class TestersTest(unittest.TestCase):

    def test_cusum(self):
        print('-- %s --' % inspect.stack()[0][3])
        for s in cusum(DATA1):
            print(s)
    
    def test_ewma(self):
        print('-- %s --' % inspect.stack()[0][3])
        for x, y, s in ewma(DATA1):
            print(x, y, s)

    def test_testers(self):
        print('-- %s --' % inspect.stack()[0][3])
        for tf, tp, h in ((pcusum, .5, 2.0),
                          (pewma, .15, .91),
                          (tcusum, 1, 2),
                          (tewma, .15, 1.4)):
            cp_k = max_ts = 0
            for i, (x, ts) in enumerate(zip(DATA1, tf(DATA1, tp))):
                if cp_k == 0:
                    if abs(ts) > h:
                        cp_k = i
                if abs(ts) > abs(max_ts):
                    max_ts = ts
            self.assertTrue(cp_k > 0 and cp_k < len(DATA1), "cp_k=%d" % cp_k)
            self.assertTrue(abs(max_ts) > h, "max_ts=%.3f" % max_ts)

    def test_testers_range(self):
        print('-- %s --' % inspect.stack()[0][3])
        base_n = 300
        test_n = 30
        sc = 2.0
        results = []
        for tf, tp, h in ((pcusum, .5, 2),
                          (pewma, .15, .91),
                          (tcusum, 1, 3.25),
                          (tewma, .15, 2)):
            test_name = "%s_%.2f_%.2f" % (tf.__name__, tp, h)
            eval = TestEvaluator(test_name)
            for cr in (.25, 1, 3):
                for _ in range(100):
                    data = [weibullvariate(1, sc) for _ in range(base_n)] + \
                           [weibullvariate(cr, sc) for _ in range(test_n)]
                    cp_k = 0
                    max_ts = 0
                    for i, ts in enumerate(tf(data, tp)):
                        if i >= base_n:
                            if cp_k == 0 and abs(ts) > h:
                                cp_k = i
                            max_ts = max(max_ts, ts, key=abs)
                    eval.count(cr, cp_k, base_n, max_ts, h)
            rpt = eval.report()
            results.append(rpt)
            self.assertTrue(rpt.fp < .02, rpt)
            self.assertTrue(rpt.fn < .3, rpt)
            self.assertTrue(rpt.ttd < 10, rpt)
        print(OpenRecord.to_text_rows(results))


if __name__ == '__main__':
    unittest.main()
