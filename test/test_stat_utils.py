import datetime as dt
from random import randint, weibullvariate
import unittest
from util.data_generator import gen_dates
from util.open_record import OpenRecord
from util.stat_utils import (
    describe,
    fit,
    mean,
    median,
    mk_trend,
    pct_diff,
    percentile,
    p50,
    p90,
    p95,
    p99,
    period_key,
    period_secs,
    period_truncate,
    periods_per_day,
    pscores,
    rankdata,
    rs_test,
    std,
    stderr,
    tcf,
    ti_test,
    t_limits,
    trim_mean,
    w_stderr,
    wx_test,
    zscores
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

    def test_describe_half(self):
        print("-- %s(%d): %s --" % get_source_info())
        ds = describe(DATA1, full_pcts=False)
        for name, value in (('n', 34),
                            ('mu', 23.469),
                            ('sd', 11.497),
                            ('p50', 23.67),
                            ('p75', 32.4225),
                            ('p90', 38.879),
                            ('p95', 40.286),
                            ('p99', 41.644),
                            ('p995', 41.697),
                            ('p999', 41.739),
                            ('p100', 41.75)):
            self.assertAlmostEqual(value, ds[name], 3, ds)

    def test_describe_full(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = list(range(300))
        ds = describe(data, full_pcts=True)
        for name, value in (('n', 300.0),
                            ('mu', 149.5),
                            ('sd', 86.747),
                            ('p00', 0.0),
                            ('p001', .299),
                            ('p005', 1.495),
                            ('p01', 2.99),
                            ('p05', 14.950),
                            ('p10', 29.900),
                            ('p25', 74.75),
                            ('p50', 149.5),
                            ('p75', 224.25),
                            ('p90', 269.1),
                            ('p95', 284.05),
                            ('p99', 296.01),
                            ('p995', 297.505),
                            ('p999', 298.701),
                            ('p100', 299)):
            self.assertAlmostEqual(value, ds[name], 3, ds)
        content = OpenRecord.to_text_cols(ds)
        self.assertEqual(19, len(content.split('\n')), content)

    def test_fit(self):
        print("-- %s(%d): %s --" % get_source_info())
        x = DATA5
        y = [x * (1 + (1 / (i + 1))) if i % 2 == 1 else (1 - (1 / (1 + i)))
             for i, x in enumerate(DATA5)]
        mape, mpe = fit(x, y)

    def testrim_mean(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(23.468, mean(DATA1), 2)
        self.assertAlmostEqual(0.7142, mean(DATA2), 2)
        self.assertAlmostEqual(9.9473, mean(DATA3), 2)
        self.assertAlmostEqual(5.6679, mean(DATA4), 2)

    def test_median(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(23.67, median(DATA1), 2)
        self.assertAlmostEqual(1.0, median(DATA2), 2)
        self.assertAlmostEqual(10.105, median(DATA3), 2)
        self.assertAlmostEqual(1.71, median(DATA4), 2)

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

    def test_percentile_one(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(33.6, percentile(list(range(3, 40, 2)), 85), 2)

    def test_percentile_many(self):
        print("-- %s(%d): %s --" % get_source_info())
        ps = percentile(list(range(5, 300, 3)), (1, 30, 75, 98))
        self.assertEqual(4, len(ps))
        self.assertAlmostEqual(7.94, ps[0], 2)
        self.assertAlmostEqual(93.2, ps[1], 2)
        self.assertAlmostEqual(225.5, ps[2], 2)
        self.assertAlmostEqual(293.12, ps[3], 2)

    def test_percentile_many_unordered(self):
        print("-- %s(%d): %s --" % get_source_info())
        ps = percentile(list(range(5, 300, 3)), (95, 77, 48, 66))
        self.assertEqual(4, len(ps))
        self.assertAlmostEqual(284.3, ps[0], 2)
        self.assertAlmostEqual(231.38, ps[1], 2)
        self.assertAlmostEqual(146.12, ps[2], 2)
        self.assertAlmostEqual(199.04, ps[3], 2)

    def test_percentile_functions(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(percentile(DATA5, 50), p50(DATA5))
        self.assertEqual(percentile(DATA5, 90), p90(DATA5))
        self.assertEqual(percentile(DATA5, 95), p95(DATA5))
        self.assertEqual(percentile(DATA5, 99), p99(DATA5))

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

    def test_pscores_fib(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = [fib(i) for i in range(1, 14)]
        for i, (p, x) in enumerate(zip(pscores(data), data)):
            if i <= 1:
                self.assertAlmostEqual(-.777, p, 2)
            elif i == 5:
                self.assertAlmostEqual(-.111, p, 2)
            elif i == 7:
                self.assertAlmostEqual(.185, p, 2)
            elif i == 12:
                self.assertAlmostEqual(.923, p, 2)

    def test_pscores_dups(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = sorted(DATA3)
        for i, (p, x) in enumerate(zip(pscores(data), data)):
            if i < 3:
                self.assertAlmostEqual(-0.869, p, 2)
            elif i == 29:
                self.assertAlmostEqual(0.967, p, 2)

    def test_rankdata(self):
        print("-- %s(%d): %s --" % get_source_info())
        for i, (x, r) in enumerate(zip(DATA3, rankdata(DATA3))):
            if i == 2:
                self.assertAlmostEqual(2.0, r, 2)
            elif i == 9:
                self.assertAlmostEqual(23.0, r, 2)

    def test_rankdata_ties(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = sorted(DATA2)
        for i, (x, r) in enumerate(zip(data, rankdata(data))):
            if i < 9:
                self.assertEqual(5.0, r)
            elif i < 18:
                self.assertEqual(14.0, r)
            else:
                self.assertEqual(20.0, r)

    def test_rs_test(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(2.049, round(rs_test(DATA1[0:25], DATA1[25:]), 3))

    def test_rs_test_ties(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(2.558, round(rs_test(DATA2[0:12], DATA2[12:]), 3))

    def test_rs_test_not_enough_data(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(0, rs_test(DATA1[:2], DATA1[2:]))

    def test_rs_test_range(self):
        print("-- %s(%d): %s --" % get_source_info())
        n = 100
        m = 15
        dss = []
        for cr in (.05, 1, 5):
            scores = []
            for _ in range(200):
                base = [weibullvariate(1, 2) for _ in range(n)]
                test = [weibullvariate(cr, 2) for _ in range(m)]
                ts = rs_test(base, test)
                scores.append(ts)
            dss.append(describe(scores, "rs_test_%.2f" % cr, full_pcts=True))
        rpt = OpenRecord.to_text_cols(dss)
        self.assertTrue(dss[0].mu < -2.5, rpt)
        self.assertTrue(abs(dss[1].mu) < .5, rpt)
        self.assertTrue(dss[2].mu > 2.5, rpt)

    def test_std(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(0, std([1, 1, 1]))
        self.assertEqual(1.63, round(std([1.2, 2.3, 4.4]), 2))

    def test_stderr(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(.94, round(stderr([1.2, 2.3, 4.4]), 2))

    def test_tcf(self):
        print("-- %s(%d): %s --" % get_source_info())
        for n, z, t in ((10, 2, 1.719),
                        (10, 3, 2.0775),
                        (100, 3, 2.923),
                        (100, 6, 5.4009)):
            self.assertAlmostEqual(t, tcf(n, z), 3)

    def test_ti_test(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(1.727, round(ti_test(DATA1[0:25], DATA1[25:]), 3))

    def test_ti_test_range(self):
        print("-- %s(%d): %s --" % get_source_info())
        n = 50
        m = 15
        dss = []
        for cr in (.5, 1, 2):
            scores = []
            for _ in range(200):
                base = [weibullvariate(1, 2) for _ in range(n)]
                test = [weibullvariate(cr, 2) for _ in range(m)]
                ts = ti_test(base, test)
                scores.append(ts)
            dss.append(describe(scores, "ti_test_%.2f" % cr, full_pcts=True))
        rpt = OpenRecord.to_text_cols(dss)
        self.assertTrue(dss[0].mu < -2.5, rpt)
        self.assertTrue(abs(dss[1].mu) < .5, rpt)
        self.assertTrue(dss[2].mu > 2.5, rpt)

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
                self.assertTrue(mean(ses) / mean(mus) < .4)

    def test_w_stderr(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(2.059, w_stderr(DATA1, .25), 3)

    def test_wx_test_pair(self):
        print("-- %s(%d): %s --" % get_source_info())
        test = list(range(1, 13))
        base = list([i + 13 if i % 3 == 0 else i for i in range(1, 13)])
        self.assertAlmostEqual(-2.3297, wx_test(test, base), 3)

    def test_wx_test_standard(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(-2.957, wx_test(DATA4, 10), 3)
        self.assertAlmostEqual(2.851, wx_test(DATA4, 1), 3)

    def test_zscores(self):
        print("-- %s(%d): %s --" % get_source_info())
        zs = zscores(DATA1)
        self.assertAlmostEqual(0.0, mean(zs), 3)
        self.assertAlmostEqual(1.0, std(zs), 3)


if __name__ == '__main__':
    unittest.main()
