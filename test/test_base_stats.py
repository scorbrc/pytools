import unittest
from util.base_stats import (
    mean,
    percentile,
    rankdata,
    std
)
from util.util_tools import get_source_info

DATA1 = [14.34, 15.27, 2.64, 11.6, 28.81, 35.01, 24.5, 25.78, 11.94, 13.95,
         22.84, 21.67, 32.45, 8.96, 15.38, 32.34, 41.75, 4.87, 4.89, 30.59,
         36.24, 10.6, 38.55, 15.29, 27.17, 28.55, 16.9, 39.67, 18.93, 22.21,
         27.81, 35.98, 41.43, 39.02]

DATA2 = [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 2, 1, 2, 2]

DATA3 = [10.81, 20.97, 0, 15.64, 11.23, 9.24, 16.53, 6.97, 11.84, 14.6,
         7.01, 11.12, 17.45, 0, 18.62, 3.44, 4.27, 4.12, 1.48, 9.4, 13.09,
         12.24, 0, 18.74, 8.22, 20.75, 12.5, 3.39, 8.48, 6.27]

DATA4 = [0.12, 0.13, 0.13, 0.14, 0.15, 0.16, 0.2, 0.23, 0.33, 0.45, 0.53,
         0.66, 0.79, 0.9, 0.98, 1.16, 1.65, 1.72, 1.87, 2.01, 2.26, 2.34,
         2.42, 3.92, 5.29, 5.93, 6.5, 11.34, 11.76, 14.66, 16.25, 23.86,
         27.64, 71.82, 79.04]


class TestBaseStats(unittest.TestCase):

    def test_mean(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(23.468, mean(DATA1), 2)
        self.assertAlmostEqual(0.7142, mean(DATA2), 2)
        self.assertAlmostEqual(9.9473, mean(DATA3), 2)

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

    def test_std(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertAlmostEqual(11.497, std(DATA1), 3)
        self.assertAlmostEqual(0.7171, std(DATA2), 3)

    def test_std_small(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(0, std([1, 1, 1]))
        self.assertAlmostEqual(1.626, std([1.2, 2.3, 4.4]), 3)
        self.assertAlmostEqual(5.520, std([1.721, 9.528]), 3)
        self.assertEqual(0, std([1.721]))


if __name__ == '__main__':
    unittest.main()
