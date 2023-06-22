import unittest
import numpy as np
from random import randint
from test_evaluator import TestEvaluator
from util.charts import chart
from util.data_generator import change, gen_cycle
from util.describer import describe
from util.hws import hws
from util.open_record import OpenRecord
from util.stat_utils import fit
from util.timer import Timer
from util.util_tools import get_source_info


class TestHws(unittest.TestCase):

    def test_hws_random(self):
        print("-- %s(%d): %s --" % get_source_info())
        day_n = 288
        data_n = day_n * 14
        test_ct = 100
        sc = 2
        for h, (low_cr, mid_cr, high_cr) in ((2, (.25, 1.0, 3.0)),):
            mapes = []
            mpes = []
            with Timer() as tm:
                test_name = "hws_%.3f_%.3f_%.3f_%.3f" % (
                    h, low_cr, mid_cr, high_cr)
                ev = TestEvaluator(test_name)
                for cr in (low_cr, mid_cr, high_cr):
                    for i in range(test_ct):
                        dates, obs = gen_cycle(1, day_n, data_n, sc=sc)
                        ci = randint(data_n - day_n // 2, data_n - day_n // 8)
                        obs = change(obs, cr, ci, data_n)
                        eps = []
                        cp_k = max_ts = 0
                        eps, scs = hws(dates, obs)
                        for t, ts in enumerate(scs):
                            if t >= data_n - day_n:
                                if abs(ts) > abs(max_ts):
                                    max_ts = ts
                                if cp_k == 0:
                                    if abs(ts) > h:
                                        cp_k = t
                        ev.count(cr, cp_k, ci, max_ts, h)
                        mape, mpe = fit(obs[:-day_n], eps[:-day_n])
                        mapes.append(mape)
                        mpes.append(mpe)
                        if i == 0:
                            chart("%s_%.3f" % (test_name, cr),
                                  dates[-day_n * 3:],
                                  (obs[-day_n * 3:],
                                   eps[-day_n * 3:]))
                rpt = ev.report()
            rpt.mpe = np.mean(mpes)
            rpt.mape = np.mean(mapes)
            rpt.millis = tm.millis / test_ct
            self.assertTrue(rpt.fp < .01, rpt)
            self.assertTrue(rpt.fn < .2, rpt)
            self.assertTrue(rpt.eff > .9, rpt)
            self.assertTrue(rpt.ttd < 20, rpt)
            self.assertTrue(rpt.millis < 100, rpt)
            self.assertTrue(abs(rpt.mpe) < 10, rpt)
            self.assertTrue(abs(rpt.mape) < 30, rpt)


if __name__ == '__main__':
    unittest.main()
