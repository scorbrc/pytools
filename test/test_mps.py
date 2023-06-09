import unittest
import inspect
from random import choice, randint
from util.data_generator import change, gen_cycle
from test_evaluator import TestEvaluator
from util.charts import chart
from util.mps import mps
from util.open_record import OpenRecord
from util.stat_utils import (
    fit,
    mean,
    median,
    trim_mean
)
from util.timer import Timer


class TestMps(unittest.TestCase):

    def test_mps(self):
        print('-- %s --' % inspect.stack()[0][3])
        count = 50
        day_n = 288
        data_n = day_n * 14
        data_sets = [gen_cycle(
            10,
            day_n,
            data_n,
            cycle='mid',
            sc=1.1
        ) for _ in range(count*3)]
        reports = []
        for h, win_mins, ts_mins in ((.94, 180, 60),
                                     (.94, 120, 60),
                                     (.94, 180, 90),
                                     (.94, 120, 90)):
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
            if False:
                self.assertTrue(abs(rpt.mpe) < 10)
                self.assertTrue(rpt.mape < 50)
                self.assertTrue(rpt.fp < .01)
                self.assertTrue(rpt.fn < .1)
                self.assertTrue(rpt.eff > .8)
                self.assertTrue(rpt.ttd < 15)
            reports.append(rpt)
        print(OpenRecord.to_text_rows(reports, digits=4))


if __name__ == '__main__':
    unittest.main()
