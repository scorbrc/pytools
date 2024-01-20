import unittest
from random import expovariate, weibullvariate
import numpy as np
import scipy.stats as ss
from util.bootstrap import repls, p_conf, t_conf
from util.stat_utils import (
    pct_diff,
    p90,
    trim_mean,
    w_stderr
)
from util.timer import Timer
from util.util_tools import get_source_info

DATA1 = [14.34, 15.27, 2.64, 11.6, 28.81, 35.01, 24.5, 25.78, 11.94, 13.95,
         22.84, 21.67, 32.45, 8.96, 15.38, 32.34, 21.75, 4.87, 4.89, 30.59,
         36.24, 10.6, 38.55, 15.29, 27.17, 28.55, 46.9, 39.67, 18.93, 22.21,
         27.81, 35.98, 41.43, 39.02]

DATA2 = [0.12, 0.13, 0.13, 0.14, 0.15, 0.16, 0.2, 0.23, 0.33, 0.45, 0.53,
         0.66, 0.79, 0.9, 0.98, 1.16, 1.65, 1.72, 1.87, 2.01, 2.26, 2.34,
         2.42, 3.92, 5.29, 5.93, 6.5, 11.34, 11.76, 14.66, 16.25, 23.86,
         27.64, 71.82, 79.04]

DATA3 = [0.39, 0.41, 0.51, 0.58, 0.64, 0.64, 0.84, 0.88, 0.97, 1.19, 2.23, 2.41,
         2.44, 2.88, 3.0, 5.4, 7.97, 19.06, 21.85, 39.07]


def gen_data(cr, sc, n):
    return [weibullvariate(cr, sc) for _ in range(n)]


class TestBootstrap(unittest.TestCase):

    def test_repls(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(2000, repls(30, 30, 2000))
        self.assertEqual(1936, repls(31))
        self.assertEqual(31, repls(1999, 30, 2000))
        self.assertEqual(30, repls(2000))

    def test_repls_half(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(1000, repls(30, 30, 1000))
        self.assertEqual(968, repls(31, 30, 1000))
        self.assertEqual(31, repls(999, 30, 1000))
        self.assertEqual(30, repls(1000, 30, 1000))

    def test_p_conf(self):
        print("-- %s(%d): %s --" % get_source_info())
        for data in (DATA1, DATA2):
            for agg_fn in (np.median, np.mean, trim_mean):
                l95s = []
                u95s = []
                l99s = []
                u99s = []
                for _ in range(30):
                    l95, u95 = p_conf(data, .95, agg_fn)
                    l95s.append(l95)
                    u95s.append(u95)
                    l99, u99 = p_conf(data, .99, agg_fn)
                    l99s.append(l99)
                    u99s.append(u99)
                rpt = "%-10s %7.3f %7.3f %7.3f %7.3f" % \
                    (agg_fn.__name__,
                     np.mean(l95s), np.mean(u95s), np.mean(l99s), np.mean(u99s))
                self.assertTrue(np.mean(l99s) <= np.mean(l95s), rpt)
                self.assertTrue(np.mean(u99s) >= np.mean(u95s), rpt)

    def test_p_conf_perf(self):
        print("-- %s(%d): %s --" % get_source_info())
        results = []
        for data_n in (20, 50, 100, 200, 500, 1000):
            data = gen_data(1, .9, data_n)
            with Timer() as tm:
                for _ in range(100):
                    p_conf(data)
            results.append((data_n, tm.secs))
        for i in range(2, len(results)):
            pcd = pct_diff(results[i][1], results[i - 1][1])
            rpt = "%6d %7.3f %7.3f%%" % (results[i][0], results[i][1], pcd)
            self.assertTrue(pcd < 15, rpt)

    def test_p_conf_range(self):
        print("-- %s(%d): %s --" % get_source_info())
        count = 100
        data_n = 100
        low_cr = .5
        mid_cr = 1
        high_cr = 2
        cp = .95
        sc = 1.1
        for agg_fn in (np.median, np.mean, p90, trim_mean):
            fp = fn = tp = tn = 0
            with Timer() as tm:
                for _ in range(count):

                    lx, ux = p_conf(gen_data(mid_cr, sc, data_n), cp, agg_fn)
                    lx0, ux0 = p_conf(gen_data(low_cr, sc, data_n), cp, agg_fn)
                    lx1, ux1 = p_conf(gen_data(mid_cr, sc, data_n), cp, agg_fn)
                    lx2, ux2 = p_conf(
                        gen_data(
                            high_cr, sc, data_n), cp, agg_fn)

                    if ux0 < lx:
                        tp += 1
                    else:
                        fn += 1

                    if lx2 > ux:
                        tp += 1
                    else:
                        fn += 1

                    if ux1 > lx:
                        tn += 1
                    else:
                        fp += 1

                    if lx1 < ux:
                        tn += 1
                    else:
                        fp += 1

            fp = fp / (count * 2)
            tp = tp / (count * 2)
            fn = fn / (count * 2)
            tn = tn / (count * 2)

            rpt = "%-8s %7.3f %7.3f %7.3f %7.3f %s" % \
                  (agg_fn.__name__, fp, tp, fn, tn, tm)
            self.assertTrue(fp < .03, rpt)
            self.assertTrue(fn < .3, rpt)

    def test_t_conf(self):
        print("-- %s(%d): %s --" % get_source_info())
        for data in (DATA1, DATA2):
            for loc_fn, var_fn in ((np.mean, ss.sem), (trim_mean, w_stderr)):
                l95s = []
                u95s = []
                l99s = []
                u99s = []
                for _ in range(30):
                    l95, u95 = t_conf(data, .95, loc_fn, var_fn)
                    l95s.append(l95)
                    u95s.append(u95)
                    l99, u99 = t_conf(data, .99, loc_fn, var_fn)
                    l99s.append(l99)
                    u99s.append(u99)
                rpt = "%-10s %-10s %7.3f %7.3f %7.3f %7.3f" % \
                    (loc_fn.__name__, var_fn.__name__,
                     np.mean(l95s), np.mean(u95s), np.mean(l99s), np.mean(u99s))
                self.assertTrue(np.mean(l99s) <= np.mean(l95s), rpt)
                self.assertTrue(np.mean(u99s) >= np.mean(u95s), rpt)

    def test_t_conf2(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = [.14, .57, 1.438, 1.55, 1.923, 1.714, 2.193, 5.582, 11.62, 15.31, 23.47]
        for _ in range(20):
            lv, uv = t_conf(data, .95)
            print(lv, uv)

    def test_t_conf_exponential(self):
        print("-- %s(%d): %s --" % get_source_info())

        lower = []
        upper = []
        for _ in range(200):
            data = [expovariate(1) for _ in range(30)]
            mu = np.mean(data)
            se = ss.sem(data)
            lower.append(mu - se * 2.75)
            upper.append(mu + se * 2.75)
        lc1 = np.mean(lower)
        uc1 = np.mean(upper)

        lower = []
        upper = []
        for _ in range(200):
            data = [expovariate(1) for _ in range(30)]
            lv, uv = t_conf(data, .99)
            lower.append(lv)
            upper.append(uv)
        lc2 = np.mean(lower)
        uc2 = np.mean(upper)

        lower = []
        upper = []
        for _ in range(200):
            data = [expovariate(1) for _ in range(30)]
            lv, uv = t_conf(data, .99, trim_mean, w_stderr)
            lower.append(lv)
            upper.append(uv)
        lc3 = np.mean(lower)
        uc3 = np.mean(upper)

        rpt = "lc1=%.3f uc1=%.3f lc2=%.3f uc2=%.3f lc3=%.3f uc3=%.3f" % \
              (lc1, uc1, lc2, uc2, lc3, uc3)
        self.assertTrue(lc2 > lc1, rpt)
        self.assertTrue(uc2 > lc2, rpt)

    def test_t_conf_perf(self):
        print("-- %s(%d): %s --" % get_source_info())
        results = []
        for data_n in (20, 50, 100, 200, 500, 1000):
            data = gen_data(1, .9, data_n)
            with Timer() as tm:
                for _ in range(100):
                    t_conf(data)
            results.append((data_n, tm.secs))
        for i in range(2, len(results)):
            pcd = pct_diff(results[i][1], results[i - 1][1])
            rpt = "%6d %7.3f %7.3f%%" % (results[i][0], results[i][1], pcd)
            self.assertTrue(pcd < 15, rpt)

    def test_t_conf_range(self):
        print("-- %s(%d): %s --" % get_source_info())
        count = 50
        data_n = 100
        low_cr = .5
        mid_cr = 1
        high_cr = 2
        cp = .95
        sc = 1.1
        for loc_fn, sem_fn in ((np.mean, ss.sem), (trim_mean, w_stderr)):
            fp = fn = tp = tn = 0
            with Timer() as tm:
                for _ in range(count):

                    lx, ux = t_conf(
                        gen_data(
                            mid_cr, sc, data_n), cp, loc_fn, sem_fn)
                    lx0, ux0 = t_conf(
                        gen_data(
                            low_cr, sc, data_n), cp, loc_fn, sem_fn)
                    lx1, ux1 = t_conf(
                        gen_data(
                            mid_cr, sc, data_n), cp, loc_fn, sem_fn)
                    lx2, ux2 = t_conf(
                        gen_data(
                            high_cr, sc, data_n), cp, loc_fn, sem_fn)

                    if ux0 < lx:
                        tp += 1
                    else:
                        fn += 1

                    if lx2 > ux:
                        tp += 1
                    else:
                        fn += 1

                    if ux1 > lx:
                        tn += 1
                    else:
                        fp += 1

                    if lx1 < ux:
                        tn += 1
                    else:
                        fp += 1

            fp = fp / (count * 2)
            tp = tp / (count * 2)
            fn = fn / (count * 2)
            tn = tn / (count * 2)

            rpt = "%-8s %-8s %7.3f %7.3f %7.3f %7.3f %s" % \
                  (loc_fn.__name__, sem_fn.__name__, fp, tp, fn, tn, tm)
            self.assertTrue(fp < .03, rpt)
            self.assertTrue(fn < .3, rpt)


if __name__ == '__main__':
    unittest.main()
