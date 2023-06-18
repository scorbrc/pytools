import unittest
from random import choice, randint
from util.data_generator import change, gen_cycle
from test_evaluator import TestEvaluator
from util.charts import chart
from util.mps import mps
from util.open_record import OpenRecord
from util.stat_utils import (
    fit,
    mean
)
from util.timer import Timer
from util.util_tools import get_source_info


class TestMps(unittest.TestCase):

    def test_mps(self):
        print("-- %s(%d): %s --" % get_source_info())
        count = 100
        day_n = 288
        data_n = day_n * 14
        data_sets = [gen_cycle(
            10,
            day_n,
            data_n,
            cycle='mid',
            sc=1.5
        ) for _ in range(count * 3)]
        for h, win_mins, ts_mins in ((.96, 180, 60),
                                     (.96, 120, 60),
                                     (.96, 180, 90),
                                     (.96, 120, 90)):
            test_name = 'mps_%d_%d' % (win_mins, ts_mins)
            eval = TestEvaluator(test_name)
            mpes = []
            mapes = []
            with Timer() as tm:
                for cr in (.25, 1.0, 3.0):
                    for i in range(count):
                        dates, values = choice(data_sets)
                        ci = randint(data_n - day_n // 2, data_n - day_n // 8)
                        obs = change(values, cr, ci, data_n)
                        eps, tss = mps(dates, obs, win_mins, ts_mins)
                        cp_k = max_ts = 0
                        for k in range(data_n - day_n, data_n):
                            if abs(tss[k]) > max_ts:
                                max_ts = tss[k]
                            if cp_k == 0:
                                if abs(tss[k]) > h:
                                    cp_k = k
                        eval.count(cr, cp_k, ci, max_ts, h)
                        mape, mpe = fit(obs[:ci], eps[:ci])
                        mpes.append(mpe)
                        mapes.append(mape)
                        if i == 0:
                            chart(test_name + "_%.3f" % cr,
                                  dates[-day_n * 3:],
                                  (obs[-day_n * 3:], eps[-day_n * 3:]))
            rpt = eval.report()
            rpt.mpe = mean(mpes)
            rpt.mape = mean(mapes)
            rpt.millis = tm.millis / (count * 3)
            self.assertTrue(abs(rpt.mpe) < 10, rpt)
            self.assertTrue(rpt.mape < 30, rpt)
            self.assertTrue(rpt.fp < .01, rpt)
            self.assertTrue(rpt.fn < .1, rpt)
            self.assertTrue(rpt.eff > .8, rpt)
            self.assertTrue(rpt.ttd < 15, rpt)


if __name__ == '__main__':
    unittest.main()
