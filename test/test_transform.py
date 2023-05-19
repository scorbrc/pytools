import unittest
import inspect
from random import weibullvariate
from util.stat_utils import describe
from util.transform import (
    fr_sqrt_trans,
    fr_log_trans,
    to_sqrt_trans,
    to_log_trans
)


class TransformTest(unittest.TestCase):

    def test_log_trans(self):
        print(inspect.stack()[0][3])
        self.assertAlmostEqual(7.4489, to_log_trans(1717), 3)
        for x, y in zip([4.8203, 8.4268, 11.3978],
                        to_log_trans((123, 4567, 89123))):
            self.assertAlmostEqual(x, y, 3)

    def test_sqrt_trans(self):
        print(inspect.stack()[0][3])
        self.assertAlmostEqual(41.4367, to_sqrt_trans(1717), 3)
        for x, y in zip([11.0905, 67.5796, 298.5348],
                        to_sqrt_trans((123, 4567, 89123))):
            self.assertAlmostEqual(x, y, 3)

    def test_log_trans_skew(self):
        print(inspect.stack()[0][3])
        x1 = [weibullvariate(1, .5) for _ in range(20000)]
        x2 = to_log_trans(x1)
        d1 = describe(x1, '1')
        d2 = describe(x2, '2')
        cv1 = d1.sd / d1.mu
        cv2 = d2.sd / d2.mu
        cr = cv1 / cv2
        self.assertTrue(cr > 1.5, cr)

    def test_sqrt_trans_skew(self):
        print(inspect.stack()[0][3])
        x1 = [weibullvariate(1, .5) for _ in range(20000)]
        x2 = to_sqrt_trans(x1)
        d1 = describe(x1, '1')
        d2 = describe(x2, '2')
        cv1 = d1.sd / d1.mu
        cv2 = d2.sd / d2.mu
        cr = cv1 / cv2
        self.assertTrue(cr > 1.5, cr)

    def test_log_trans_and_back(self):
        print(inspect.stack()[0][3])
        for x in (0, 1, 2, 4, 8, 16, 32, 64, 2**31):
            self.assertAlmostEqual(x, fr_log_trans(to_log_trans(x)), 2)

    def test_sqrt_trans_and_back(self):
        print(inspect.stack()[0][3])
        for x in (0, 1, 2, 4, 8, 16, 32, 64, 2**31):
            self.assertAlmostEqual(x, fr_sqrt_trans(to_sqrt_trans(x)), 2)


if __name__ == '__main__':
    unittest.main()
