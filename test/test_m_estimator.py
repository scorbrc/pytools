import unittest
import inspect
from random import weibullvariate
from util.m_estimator import m_estimate, m_1est
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

class MEstimatorTest(unittest.TestCase):

    def test_m_estimate_1a(self):
        print('-' * 8, inspect.stack()[0][3])
        me, se, wt = m_estimate(DATA1, 3)
        self.assertTrue(me < mean(DATA1))
        self.assertAlmostEqual(4.4194, me, 3)
        self.assertAlmostEqual(0.8814, se, 3)
        self.assertEqual(1, wt[24])
        self.assertAlmostEqual(0.8467, wt[25], 3)

    def test_m_estimate_1b(self):
        print('-' * 8, inspect.stack()[0][3])
        me, se, wt = m_estimate(DATA1, 4)
        self.assertTrue(me < mean(DATA1))
        self.assertAlmostEqual(4.984, me, 3)
        self.assertAlmostEqual(1.0605, se, 3)
        self.assertEqual(1, wt[24])
        self.assertAlmostEqual(0.992, wt[25], 3)

    def test_m_estimate_2(self):
        print('-' * 8, inspect.stack()[0][3])
        me, se, wt = m_estimate(DATA2, 2)
        self.assertTrue(me < mean(DATA2))
        self.assertAlmostEqual(2.9726, me, 3)
        self.assertAlmostEqual(0.2734, se, 3)
        wt = sorted(wt)
        self.assertAlmostEqual(0.8415, wt[7], 3)
        self.assertEqual(1, wt[8])
        self.assertEqual(1, wt[24])
        self.assertAlmostEqual(1.384, wt[25], 3)

    def test_m_estimate_3(self):
        print('-' * 8, inspect.stack()[0][3])
        me, se, wt = m_estimate(DATA3, 4)
        self.assertAlmostEqual(3.4289, me, 3)
        self.assertAlmostEqual(0.2870, se, 3)
        self.assertEqual(1, wt[3])
        self.assertEqual(1, wt[24])
        self.assertAlmostEqual(1.9144, wt[2], 3)
        self.assertAlmostEqual(0.27884, wt[25], 3)

    def test_m_estimate_range(self):
        print('-' * 8, inspect.stack()[0][3])
        data_n = 30
        for sc in (1, .75, .5):
            for cf in (4, 3, 2):
                mes = []
                ses = []
                with Timer() as tm:
                    for _ in range(1000):
                        data = [weibullvariate(1, sc) for _ in range(data_n)]
                        me, se, _ = m_estimate(data, cf)
                        mes.append(me)
                        ses.append(se)
                print("%7.3f %7.3f %7.3f %7.3f %7.4f" %
                      (sc, cf, mean(mes), mean(ses) / mean(mes), tm.secs))


if __name__ == '__main__':
    unittest.main()
