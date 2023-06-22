import datetime as dt
from random import randint, weibullvariate
import unittest
import numpy as np
from util.data_generator import gen_dates
from util.describer import describe
from util.open_record import OpenRecord
from util.stat_utils import (
    fit,
    mk_trend,
    pct_diff,
    p50,
    p90,
    p95,
    p99,
    period_key,
    period_secs,
    period_truncate,
    periods_per_day,
    t_limits,
    trim_mean,
    w_stderr,
    wx_test
)
from util.timer import Timer
from util.util_tools import get_source_info


DATA1 = [14.34, 15.27, 2.64, 11.6, 28.81, 35.01, 24.5, 25.78, 11.94, 13.95,
         22.84, 21.67, 32.45, 8.96, 15.38, 32.34, 41.75, 4.87, 4.89, 30.59,
         36.24, 10.6, 38.55, 15.29, 27.17, 28.55, 16.9, 39.67, 18.93, 22.21,
         27.81, 35.98, 41.43, 39.02]

DATA2 = [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 2, 1, 2, 2]

DATA3 = [10.81, 20.97, 0, 15.64, 11.23, 9.24, 16.53, 6.97, 11.84, 14.6,
         7.01, 11.12, 17.45, 0, 18.62, 3.44, 4.27, 4.12, 1.48, 9.4, 13.09,
         12.24, 0, 18.74, 8.22, 20.75, 12.5, 3.39, 8.48, 6.27]

DATA4 = [0.39, 0.41, 0.51, 0.58, 0.64, 0.64, 0.84, 0.88, 0.97, 1.19, 2.23, 2.41,
         2.44, 2.88, 3.0, 5.4, 7.97, 19.06, 21.85, 39.07]

DATA5 = [0.74, 0.82, 0.11, 1.09, 0.74, 0.25, 0.56, 0.66, 0.63, 0.14, 0.68,
         0.04, 0.96, 1.2, 1.02, 1.71, 0.85, 1.34, 0.54, 0.77, 4.74, 5.86,
         3.72, 3.81, 3.75, 4.94, 6.12, 5.88, 5.63, 4.36, 7.21, 0.08, 0.89,
         1.91, 3.42, 0.71, 0.41, 0.04, 0.19, 0.39]


def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n - 1) + fib(n - 2)


class TestStatUtils(unittest.TestCase):

    def test_fit(self):
        print("-- %s(%d): %s --" % get_source_info())
        x = DATA5
        y = [x * (1 + (1 / (i + 1))) if i % 2 == 1 else (1 - (1 / (1 + i)))
             for i, x in enumerate(DATA5)]
        mape, mpe = fit(x, y)

    def test_mk_trend(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(2.46, round(mk_trend(DATA1), 2))
        self.assertEqual(3.52, round(mk_trend(DATA2), 2))

    def test_mk_trend_range(self):
        print("-- %s(%d): %s --" % get_source_info())
        names = []
        dss = []
        for n in (50, 100, 200):
            tss = []
            for _ in range(100):
                data = [weibullvariate(1, 1) * (i / n) * 2 for i in range(n)]
                tss.append(mk_trend(data))
            dss.append(describe(tss))
            names.append(str(n))
        rpt = OpenRecord.to_text_cols(dss)
        self.assertTrue(dss[1].mu > dss[0].mu, rpt)
        self.assertTrue(dss[2].mu > dss[1].mu, rpt)

    def test_pct_diff(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(0, pct_diff(1, 1))
        self.assertEqual(-200.0, pct_diff(0, 1))
        self.assertEqual(200.0, pct_diff(1, 0))
        self.assertEqual(-27.603, round(pct_diff(1.78, 2.35), 3))
        self.assertEqual(73.684, round(pct_diff(78, 36), 3))

    def test_period_key(self):
        print("-- %s(%d): %s --" % get_source_info())
        pk = period_key(dt.datetime.now())
        self.assertEqual(3, len(pk.split(':')))
        dty, hr, min = pk.split(':')
        self.assertTrue(int(min) >= 0, pk)
        self.assertTrue(int(min) < 60, pk)
        self.assertTrue(int(hr) > 0, pk)
        self.assertTrue(int(hr) < 24, pk)
        self.assertTrue(dty == 'WD' or dty == 'WE', pk)

    def test_period_truncate(self):
        print("-- %s(%d): %s --" % get_source_info())
        now = dt.datetime.now()
        dates0 = [now - dt.timedelta(minutes=1440 - i) for i in range(1440)]
        dates1 = set([period_truncate(d, 600) for d in dates0])
        self.assertTrue(len(dates1) >= 143 and len(dates1) <= 146)

    def test_period_truncate_range(self):
        print("-- %s(%d): %s --" % get_source_info())
        psecs = 60 * 60
        msecs = psecs // 2
        intervals = []
        now = dt.datetime.now()
        for i in range(100):
            d0 = now + dt.timedelta(seconds=randint(-msecs, msecs))
            d1 = period_truncate(d0, psecs)
            intervals.append((d1 - d0).total_seconds())
        ds = describe(intervals, 'intervals', full_pcts=True)
        self.assertTrue(ds.p00 < -msecs * .85, ds)
        self.assertTrue(ds.p100 > msecs * .85, ds)

    def test_period_secs(self):
        print("-- %s(%d): %s --" % get_source_info())
        dates = (dt.datetime(2022, 6, 15, 12),
                 dt.datetime(2022, 6, 15, 12, 5),
                 dt.datetime(2022, 6, 15, 12, 10),
                 dt.datetime(2022, 6, 15, 12, 15),
                 dt.datetime(2022, 6, 15, 12, 20),
                 dt.datetime(2022, 6, 15, 12, 25))
        self.assertEqual(300, period_secs(dates))

    def test_periods_per_day(self):
        print("-- %s(%d): %s --" % get_source_info())
        day_n = 288
        dates = gen_dates(day_n, day_n * 3)
        self.assertEqual(day_n, periods_per_day(dates))

    def test_periods_per_day_short(self):
        print("-- %s(%d): %s --" % get_source_info())
        day_n = 288
        dates = gen_dates(day_n, day_n - 1)
        self.assertEqual(day_n, periods_per_day(dates))

    def test_t_limits(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual((7, 23), t_limits(30, .25))
        self.assertEqual((9, 21), t_limits(30, .33))
        self.assertEqual((1, 29), t_limits(30, 0))
        self.assertEqual((1, 2), t_limits(3, .25))
        with self.assertRaises(ValueError):
            t_limits(2, .25)

    def test_trim_mean(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(23.533, trim_mean(DATA1), 2)
        self.assertAlmostEqual(0.6153, trim_mean(DATA2), 2)
        self.assertAlmostEqual(9.836, trim_mean(DATA3), 2)
        self.assertAlmostEqual(1.96, trim_mean(DATA4), 2)

    def test_robust(self):
        print("-- %s(%d): %s --" % get_source_info())
        data_n = 30
        for sc in (1, .75):
            for tp in (.1, .2, .3):
                mus = []
                ses = []
                for _ in range(1000):
                    data = [weibullvariate(1, sc) for _ in range(data_n)]
                    mu = trim_mean(data, tp)
                    se = w_stderr(data, tp)
                    mus.append(mu)
                    ses.append(se)
                self.assertTrue(np.mean(ses) / np.mean(mus) < .4)

    def test_w_stderr(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(2.059, w_stderr(DATA1, .25), 3)


if __name__ == '__main__':
    unittest.main()
