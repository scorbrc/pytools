import unittest
from copy import deepcopy
from random import choice
from util.ab_tester import ab_test
from util.data_generator import gen_cycle, gen_flat
from test_evaluator import TestEvaluator
from util.util_tools import get_source_info


class TestABTester(unittest.TestCase):

    def test_ab_tester_cycle(self):
        print("-- %s(%d): %s --" % get_source_info())
        count = 50
        day_n = 288
        data_n = day_n * 14
        test_n = day_n // 24
        sc = .9

        data_sets = [gen_cycle(5, day_n, day_n * 14, sc=sc, cycle='mid')
                     for _ in range(count * 3)]

        for iters_n in (20,):
            for dtn, hn, min_pcd, fail_h in ((3, 2, 5, 3),
                                             (3, 3, 5, 3),
                                             (3, 6, 5, 3)):
                name = "ab_test_cycle_%d_%d_%.3f_%.3f_%d" % (
                    dtn, hn, min_pcd, fail_h, iters_n)
                eval = TestEvaluator(name)
                for cr in (.5, 1.0, 2.0):
                    for _ in range(count):
                        dates, orig_values = choice(data_sets)
                        values = deepcopy(orig_values)
                        for i in range(data_n - test_n, data_n):
                            values[i] *= cr
                        test, data_set = ab_test(
                            name,
                            dates,
                            values,
                            test_n=test_n,
                            day_type_n=dtn,
                            hour_n=hn,
                            lower_h=-fail_h,
                            upper_h=fail_h
                        )
                        eval.count_test(cr, test)
                rpt = eval.report()
                self.assertTrue(rpt.fp < .02, rpt)
                self.assertTrue(rpt.fn < .5, rpt)
                self.assertTrue(rpt.eff > .5, rpt)
                self.assertTrue(rpt.fn < .5, rpt)
                self.assertTrue(rpt.eff > .5, rpt)

    def test_ab_tester_cycle_low(self):
        print("-- %s(%d): %s --" % get_source_info())
        count = 50
        day_n = 1440
        data_n = day_n * 14
        test_n = 15
        sc = .9

        data_sets = [gen_cycle(5, day_n, day_n * 14, sc=sc, cycle='low')
                     for _ in range(count * 3)]

        for dtn, hn, min_pcd, fail_h in ((3, 2, 5, 2.75),
                                         (3, 3, 5, 2.75),
                                         (3, 4, 5, 2.75)):
            name = "ab_test_cycle_low_%d_%d_%.3f_%.3f" % \
                (dtn, hn, min_pcd, fail_h)
            eval = TestEvaluator(name)
            for cr in (.5, 1.0, 2.0):
                for _ in range(count):
                    dates, orig_values = choice(data_sets)
                    values = deepcopy(orig_values)
                    for i in range(data_n - test_n, data_n):
                        values[i] *= cr
                    test, data_set = ab_test(
                        name,
                        dates,
                        values,
                        test_n=test_n,
                        day_type_n=dtn,
                        hour_n=hn,
                        lower_h=-fail_h,
                        upper_h=fail_h
                    )
                    eval.count_test(cr, test)
            rpt = eval.report()
            self.assertTrue(rpt.fp < .02, rpt)
            self.assertTrue(rpt.fn < .5, rpt)
            self.assertTrue(rpt.eff > .5, rpt)
            self.assertTrue(rpt.fn < .5, rpt)
            self.assertTrue(rpt.eff > .5, rpt)

    def test_ab_tester_flat(self):
        print("-- %s(%d): %s --" % get_source_info())
        count = 50
        day_n = 288
        data_n = day_n * 14
        test_n = day_n // 24
        sc = 1.5

        data_sets = [gen_flat(5, day_n, day_n * 14, sc=sc)
                     for _ in range(count * 3)]

        for dtn, hn, min_pcd, fail_h in ((3, 1, 5, 2.25),
                                         (3, 2, 5, 2.25),
                                         (3, 3, 5, 2.25)):
            name = "ab_test_flat_%d_%d_%.3f_%.3f" % \
                (dtn, hn, min_pcd, fail_h)
            eval = TestEvaluator(name)
            for cr in (.35, 1.0, 2.5):
                for _ in range(count):
                    dates, orig_values = choice(data_sets)
                    values = deepcopy(orig_values)
                    for i in range(data_n - test_n, data_n):
                        values[i] *= cr
                    test, data_set = ab_test(
                        name,
                        dates,
                        values,
                        test_n=test_n,
                        day_type_n=dtn,
                        hour_n=hn,
                        lower_h=-fail_h,
                        upper_h=fail_h
                    )
                    eval.count_test(cr, test)
            rpt = eval.report()
            self.assertTrue(rpt.fp < .05, rpt)
            self.assertTrue(rpt.fn < .5, rpt)
            self.assertTrue(rpt.eff > .5, rpt)
            self.assertTrue(rpt.fn < .5, rpt)
            self.assertTrue(rpt.eff > .5, rpt)


if __name__ == '__main__':
    unittest.main()
