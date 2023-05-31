import unittest
import inspect
from random import weibullvariate
from test_evaluator import TestEvaluator
from util.open_record import OpenRecord
from util.stat_utils import describe
from util.testers import (
    pcusum,
    pewma,
    tcusum,
    tewma
)
from util.timer import Timer


DATA1 = [5.06, 4.2, 4.55, 6.08, 1.65, 7.33, 4.87, 4.41, 3.27, 8.54, 4.77,
         3.09, 1.62, 5.61, 5.04, 3.72, 2.64, 2.94, 1.12, 1.01, 2.92, 7.71,
         2.51, 6.42, 6.96, 1.11, 0.63, 5.58, 2.41, 6.98, 8.06, 13.44, 15.05,
         3.84, 16.69, 18.65, 24.11, 16.58, 16.39, 28.15, 14.01, 5.13, 14.14,
         26.98, 17.94, 11.75, 15.69, 10.85, 27.27, 14.54]

DATA2 = [2.16, 3.48, 1.79, 4.32, 2.21, 5.93, 3.0, 4.16, 4.57, 2.46, 5.67,
         6.14, 2.79, 3.83, 6.61, 5.36, 4.18, 3.05, 3.44, 4.48, 6.52, 3.08,
         1.69, 4.15, 9.62, 7.09, 4.36, 3.83, 6.14, 3.95, 0.51, 0.4, 0.76, 0.5,
         0.91, 0.17, 0.65, 1.33, 0.51, 0.14, 1.23, 1.05, 0.6, 0.18, 0.12, 1.22,
         1.61, 0.14, 1.3, 0.61]

class TestersTest(unittest.TestCase):

    def test_testers(self):
        print('-- %s --' % inspect.stack()[0][3])
        base_n = 30
        for tst, tp, h, n in ((pewma, .33, .92, 6),
                                (pcusum, .5, 2, 6),
                                (tewma, .33, 2, 2),
                                (tcusum, 1, 3, 6)):
            for i, ts in enumerate(tst(DATA1, base_n, tp)):
                if abs(ts) > h:
                    self.assertEqual(n, i, tst.__name__)
                    break

    def test_testers_range(self):
        print('-- %s --' % inspect.stack()[0][3])
        count = 200
        base_n = 300
        test_n = 30
        sc = 1.5
        reports = []
        for tst, tp, h in ((pcusum, .65, 1.25),
                           (pewma, .15, .92),
                           (tcusum, .5, 2.5),
                           (tewma, .15, 2)):
            test_name = "%s_%.2f_%.2f" % (tst.__name__, tp, h)
            eval = TestEvaluator(test_name)
            for cr in (.25, 1, 3):
                for _ in range(count):
                    data = [weibullvariate(1, sc) for _ in range(base_n)] + \
                           [weibullvariate(cr, sc) for _ in range(test_n)]
                    cp_k = max_ts = 0
                    for i, ts in enumerate(tst(data, base_n, tp)):
                        if cp_k == 0:
                            if abs(ts) > h:
                                cp_k = i + base_n
                        if abs(ts) > abs(max_ts):
                            max_ts = ts
                    eval.count(cr, cp_k, base_n, max_ts, h)
            rpt = eval.report()
            reports.append(rpt)
            self.assertTrue(rpt.fp < .01, rpt)
            self.assertTrue(rpt.fn < .1, rpt)
            self.assertTrue(rpt.ttd < 15, rpt)
        print(OpenRecord.to_text_rows(reports))


if __name__ == '__main__':
    unittest.main()
