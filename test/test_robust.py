import unittest
import inspect
from random import weibullvariate
from util.robust import (
    est,
    m_est,
    trim_est
)
from util.stat_utils import mean, stderr
from util.timer import Timer

DATA1 = [0.11, 0.21, 0.24, 0.24, 0.26, 0.28, 0.31, 0.36, 0.37, 0.38, 0.57, 0.7,
         0.71, 1.44, 3.0, 3.1, 4.03, 4.16, 4.96, 6.52, 8.22, 8.57, 9.62, 10.79,
         11.02, 14.34, 20.54, 22.18, 28.56, 54.58]

DATA2 = [0.74, 0.11, 0.38, 0.71, 0.41, 4.29, 4.91, 4.05, 4.82, 3.6, 3.67, 4.73,
         3.05, 4.89, 4.04, 4.99, 4.28, 3.86, 3.71, 3.38, 3.4, 3.99, 3.8, 4.04,
         3.39, 3.75, 3.69, 4.97, 3.07, 3.18]

DATA3 = [0.46, 0.17, 0.4, 0.71, 0.53, 3.07, 3.58, 4.53, 3.1, 4.22, 4.09, 4.1,
         3.49, 3.45, 3.77, 4.24, 4.99, 4.24, 3.09, 4.58, 4.91, 3.84, 3.2, 4.31,
         3.75, 15.12, 16.68, 16.37, 16.85, 17.64]

DATA4 = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]

DATA5 = [0.2, 0.11, 0.68, 0.21, 0.65,
         4.56, 3.91, 3.59, 4.07, 3.45, 4.43, 3.12, 3.24, 4.05, 4.17,
         3.29, 4.08, 3.22, 3.64, 4.17, 4.06, 3.31, 4.33, 4.34, 3.61,
         13.45, 13.59, 11.68, 13.59, 12.4]

class RobustTest(unittest.TestCase):

    def test_est(self):
        print('-' * 8, inspect.stack()[0][3])
        values = []
        for data, exp_mu, exp_se in ((DATA1, 7.346, 2.115),
                                     (DATA2, 3.397, 0.264),
                                     (DATA3, 5.449, 0.956),
                                     (DATA4, 50.667, 20.787),
                                     (DATA5, 4.773, 0.724)):
            mu, se = est(data)
            self.assertAlmostEqual(exp_mu, mu, 3)
            self.assertAlmostEqual(exp_se, se, 3)

    def test_m_est(self):
        print('-' * 8, inspect.stack()[0][3])
        values = []
        for data, exp_mu, exp_se in ((DATA1, 3.59, 0.709),
                                     (DATA2, 2.675, 0.358),
                                     (DATA3, 2.936, 0.347),
                                     (DATA4, 20.587, 6.15),
                                     (DATA5, 2.378, 0.41)):
            mu, se = m_est(data)
            self.assertAlmostEqual(exp_mu, mu, 3)
            self.assertAlmostEqual(exp_se, se, 3)

    def test_trim_est(self):
        print('-' * 8, inspect.stack()[0][3])
        values = []
        for data, exp_mu, exp_se in ((DATA1, 3.767, 1.061),
                                     (DATA2, 3.733, 0.142),
                                     (DATA3, 3.916, 0.173),
                                     (DATA4, 28.5, 19.973),
                                     (DATA5, 3.831, 0.126)):
            mu, se = trim_est(data)
            self.assertAlmostEqual(exp_mu, mu, 3)
            self.assertAlmostEqual(exp_se, se, 3)

    def test_trim_est_example(self):
        print('-' * 8, inspect.stack()[0][3])
        data = list(range(1, 9))
        mu, se = trim_est(data)
        self.assertAlmostEqual(4.5, mu, 3)
        self.assertAlmostEqual(1.0333, se, 3)


    def test_m_est_range(self):
        print('-' * 8, inspect.stack()[0][3])
        data_n = 30
        for sc in (1, .75, .5):
            last_mu = last_se = None
            for cf in (3, 2):
                means = []
                stderrs = []
                with Timer() as tm:
                    for _ in range(1000):
                        data = [weibullvariate(1, sc) for _ in range(data_n)]
                        me, se = m_est(data, cf)
                        means.append(me)
                        stderrs.append(se)
                mu = mean(means)
                se = mean(stderrs)
                rpt = "%7.3f %7.3f %7.3f %7.3f %7.4f" % \
                      (sc, cf, mu, se / mu, tm.secs)
                if last_mu is not None:
                    self.assertTrue(mu < last_mu, rpt)
                if last_se is not None:
                    self.assertTrue(se < last_se, rpt)

    def test_trim_est_range(self):
        print('-' * 8, inspect.stack()[0][3])
        data_n = 30
        for sc in (1, .75, .5):
            last_mu = last_se = None
            for p in (.1, .3):
                means = []
                stderrs = []
                with Timer() as tm:
                    for _ in range(1000):
                        data = [weibullvariate(1, sc) for _ in range(data_n)]
                        me, se = trim_est(data, p)
                        means.append(me)
                        stderrs.append(se)
                mu = mean(means)
                se = mean(stderrs)
                rpt = "%7.3f %7.3f %7.3f %7.3f %7.4f" % \
                      (sc, p, mu, se / mu, tm.secs)
                if last_mu is not None:
                    self.assertTrue(mu < last_mu, rpt)
                if last_se is not None:
                    self.assertTrue(se < last_se, rpt)


if __name__ == '__main__':
    unittest.main()
