import unittest
from collections import defaultdict
import json
from random import choice, randint, weibullvariate
from util.changepoint import (
    rs_cpd,
    rs_cpd_multi,
    ti_cpd,
    ti_cpd_multi
)
from util.data_generator import gen_cycle
from util.open_record import OpenRecord
from util.stat_utils import describe, pct_diff
from util.timer import Timer
from util.util_tools import get_source_info


def count_cpd(cr, cp_k, ci, max_ts, h, counts, tdd):
    counts['ct'] += 1
    if max_ts > h:
        if cr > 1:
            counts['tp'] += 1
            tdd.append(cp_k - ci)
        else:
            counts['fp'] += 1
    elif max_ts < -h:
        if cr < 1:
            counts['tp'] += 1
            tdd.append(cp_k - ci)
        else:
            counts['fp'] += 1
    else:
        if cr != 1:
            counts['fn'] += 1
        else:
            counts['tn'] += 1
            tdd.append(0)


def report(test_name, dss_ts, dss_td, counts):
    if len(dss_ts) < 3:
        raise ValueError("Need at least 3 descs.")
    return OpenRecord(
        test_name=test_name,
        lp01=dss_ts[0].p005,
        lp99=dss_ts[0].p995,
        mp01=dss_ts[1].p005,
        mp99=dss_ts[1].p995,
        up01=dss_ts[2].p005,
        up99=dss_ts[2].p995,
        tp=counts['tp'] / counts['ct'],
        fp=counts['fp'] / counts['ct'],
        tn=counts['tn'] / counts['ct'],
        fn=counts['fn'] / counts['ct'],
        ttd=(dss_td[0].mu + dss_td[2].mu) / 2)


DATA = [1.28, 1.15, 2.28, 1.98, 1.08, 0.56, 1.38, 2.29, 1.49, 1.11, 1.49,
        1.99, 1.84, 1.79, 2.05, 1.31, 0.96, 1.93, 2.48, 0.87, 1.34, 2.0,
        1.67, 1.99, 0.72, 1.54, 2.01, 2.34, 1.26, 2.21, 2.66, 5.62, 3.78,
        5.02, 7.48, 6.89, 2.92, 3.78, 3.1, 4.77, 3.92, 3.15, 5.27, 4.13,
        6.7, 3.49, 5.48, 5.81, 3.3, 3.33]


class ChangepointTest(unittest.TestCase):

    def test_changepoint_rs_cpd(self):
        print("-- %s(%d): %s --" % get_source_info())
        max_ts, cp_k = rs_cpd(DATA)
        self.assertAlmostEqual(3.0695, max_ts, 3)
        self.assertEqual(30, cp_k)

    def test_changepoint_ti_cpd(self):
        print("-- %s(%d): %s --" % get_source_info())
        max_ts, cp_k = ti_cpd(DATA)
        self.assertAlmostEqual(2.933, max_ts, 3)
        self.assertEqual(31, cp_k)

    def test_changepoint_multi_but_with_one_changepoint(self):
        print("-- %s(%d): %s --" % get_source_info())
        data_n = 500
        results = []
        for cpd_fn, sc, h in ((rs_cpd_multi, 1.5, 2.5), (rs_cpd_multi, 1.0, 2.5),
                              (ti_cpd_multi, 2.0, 3.0), (ti_cpd_multi, 1.5, 3.0)):
            test_name = "%s_%.2f_%.3f" % (cpd_fn.__name__, sc, h)
            dss_ts = []
            dss_td = []
            counts = defaultdict(int)
            with Timer() as tm:
                for cr in (.25, 1, 3):
                    max_tss = []
                    tdd = []
                    for i in range(50):
                        ci = randint(int(data_n / 2), data_n - 10)
                        data = [weibullvariate(1, sc) for _ in range(ci)] + \
                               [weibullvariate(cr, sc)
                                for _ in range(data_n - ci)]
                        cps = cpd_fn(data, h)
                        if len(cps):
                            cp = cps[0]
                            max_tss.append(cp.ts)
                            count_cpd(cr, cp.ci, ci, cp.ts, h, counts, tdd)
                    dss_ts.append(describe(
                        max_tss, 'tss_%s_%.2f' % (test_name, cr), full_pcts=True))
                    dss_td.append(describe(
                        tdd, 'tdd_%s_%.2f' % (test_name, cr), full_pcts=True))
            rpt = report(test_name, dss_ts, dss_td, counts)
            rpt.secs = tm.secs
            self.assertTrue(rpt.fp < .05, rpt)
            self.assertTrue(rpt.fn < .2, rpt)
            results.append(rpt)

    def test_rs_cpd_multi(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = [1.68, 0.95, 3.53, 5.06, 0.81, 2.88, 1.68, 3.79, 2.93, 1.12,
                1.36, 0.15, 1.62, 0.5, 0.3, 1.46, 2.63, 1.85, 2.51, 3.2, 5.77,
                5.53, 3.18, 0.55, 1.3, 4.99, 4.69, 5.55, 1.77, 4.19, 1.21,
                3.06, 0.08, 4.93, 4.74, 2.93, 0.48, 1.35, 1.35, 4.98, 3.15,
                3.95, 4.73, 4.0, 5.42, 5.69, 5.06, 1.94, 4.33, 2.92, 1.35,
                0.73, 1.99, 0.91, 0.58, 1.05, 1.18, 1.51, 0.88, 0.93, 0.91,
                0.49, 1.92, 1.97, 1.52, 1.97, 1.13, 1.66, 0.35, 1.22, 0.35,
                1.86, 1.02, 0.74, 1.62, 1.04, 1.78, 1.89, 0.12, 1.86, 0.83,
                0.52, 0.41, 0.98, 1.11, 1.28, 1.89, 1.17, 1.72, 0.87, 0.29,
                1.51, 1.12, 1.64, 0.47, 0.29, 1.02, 0.38, 1.85, 0.09, 1.07,
                1.52, 2.46, 5.52, 0.53, 2.17, 5.39, 2.31, 5.42, 1.48, 5.02,
                5.42, 1.05, 4.72, 3.23, 1.77, 3.3, 1.26, 1.55, 1.59, 1.36,
                4.64, 5.67, 1.92, 5.1, 2.25, 5.41, 2.68, 0.96, 3.82, 2.9,
                0.36, 2.32, 4.36, 1.34, 2.72, 5.16, 1.36, 3.45, 3.19, 1.95,
                3.56, 3.88, 2.78, 3.09, 4.54, 4.72, 1.94, 3.33, 5.81]
        cps = rs_cpd_multi(data, 2)
        self.assertEqual(2, len(cps))
        self.assertEqual(-2.455, round(cps[0].ts, 3))
        self.assertEqual(50, cps[0].ci, 2)
        self.assertEqual(2.226, round(cps[1].ts, 3))
        self.assertEqual(102, cps[1].ci, 2)

    def test_ti_cpd_multi(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = [0.9, 1.43, 0.94, 0.35, 0.74, 0.54, 0.81, 0.61, 1.0, 0.25, 1.27,
                0.51, 1.78, 1.33, 1.02, 0.37, 0.29, 0.07, 0.57, 1.58, 0.4, 0.4,
                1.66, 1.51, 1.18, 0.12, 0.83, 0.58, 1.07, 0.74, 0.78, 0.37, 1.3,
                0.97, 1.28, 1.17, 1.49, 0.49, 1.33, 0.79, 1.03, 1.09, 1.95, 0.85,
                1.16, 0.8, 0.73, 1.15, 0.95, 1.2, 4.57, 4.75, 12.59, 4.17, 16.82,
                5.25, 14.0, 4.03, 10.76, 14.18, 8.11, 5.83, 9.77, 6.0, 3.5, 4.13,
                12.47, 13.74, 6.7, 11.64, 6.3, 6.9, 4.81, 4.08, 1.85, 6.33, 9.2,
                11.43, 10.95, 2.52, 2.87, 6.95, 6.59, 10.14, 9.99, 7.76, 4.56,
                4.25, 14.26, 7.87, 3.7, 2.83, 9.71, 7.8, 8.72, 8.83, 7.74, 1.85,
                6.29, 9.3, 0.16, 0.7, 0.66, 0.83, 1.13, 1.16, 2.27, 1.97, 0.88,
                0.43, 0.64, 0.91, 0.92, 1.38, 1.23, 0.37, 0.91, 0.98, 0.82,
                1.28, 0.81, 1.23, 0.73, 1.94, 0.83, 0.72, 1.02, 0.3, 0.88, 2.19,
                0.54, 0.78, 0.86, 0.78, 0.41, 0.96, 0.74, 1.1, 1.01, 0.58, 0.45,
                0.78, 0.56, 1.23, 1.3, 0.58, 0.85, 1.63, 0.99, 0.26]
        cps = ti_cpd_multi(data, 1.5)
        self.assertEqual(2, len(cps))
        self.assertEqual(2.712, round(cps[0].ts, 3))
        self.assertEqual(50, cps[0].ci, 2)
        self.assertEqual(-4.021, round(cps[1].ts, 3))
        self.assertEqual(100, cps[1].ci, 2)

    def test_rs_cpd_multi_up_and_down(self):
        print("-- %s(%d): %s --" % get_source_info())
        day_n = 288
        data_n = day_n * 7
        count = 30
        for sc, h, ci, cn, cr in ((1.5, 3.25, data_n // 2, day_n, 3), ):
            success = 0
            for i in range(count):
                data = [weibullvariate(1, sc) for _ in range(ci)] + \
                       [weibullvariate(cr, sc) for _ in range(ci, ci + cn)] + \
                       [weibullvariate(1, sc) for _ in range(ci + cn, data_n)]
                cps = rs_cpd_multi(data, h)
                if len(cps) >= 2:
                    if pct_diff(ci, cps[0].ci) < 15:
                        if pct_diff(ci + cn, cps[1].ci) < 15:
                            success += 1
            self.assertTrue(success / count > .7,
                            "success=%d, count=%d" % (success, count))

    def test_rs_cpd_multi_up_and_down_cycle(self):
        print("-- %s(%d): %s --" % get_source_info())
        day_n = 288
        data_n = day_n * 30
        sc = 1.5
        h = 5
        count = 20
        for cpd_fn in (rs_cpd_multi, ti_cpd_multi):
            match_count = 0
            for i in range(20):
                dates, data = gen_cycle(10, day_n, data_n, sc=sc, cycle='low')
                spec = []
                si = 0
                last_cr = 0
                for _ in range(randint(2, 4)):
                    while True:
                        cr = choice((.25, .5, 2.0, 3.0))
                        if cr != last_cr:
                            break
                    last_cr = cr
                    si = randint(si + day_n // 2, si + day_n * 3)
                    ei = min(
                        randint(
                            si +
                            day_n,
                            si +
                            day_n *
                            3) +
                        day_n //
                        2,
                        data_n)
                    if ei - si > day_n // 2:
                        spec.append(OpenRecord(cr=cr, si=si, ei=ei, matches=0))
                        for j in range(si, ei):
                            data[j] *= cr
                    si = ei
                cps = cpd_fn(data, h)
                for cp in cps:
                    cp.matched = False
                    for sp in spec:
                        if (abs(pct_diff(cp.ci, sp.si)) < 10 or
                                abs(pct_diff(cp.ci, sp.ei)) < 10):
                            cp.matched = True
                            sp.matches += 1
                            break
                cp_not_matched = sum([1 for cp in cps if not cp.matched])
                sp_not_matched = sum([1 for sp in spec if sp.matches == 0])
                if cp_not_matched > 0 or sp_not_matched > 0:
                    print("Test %d" % i)
                    print(json.dumps({'spec': spec, 'cps': cps}, indent=4))
                else:
                    match_count += 1
            self.assertTrue(match_count / count > .9)


if __name__ == '__main__':
    unittest.main()
