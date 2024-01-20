import unittest
from random import choice, weibullvariate
import numpy as np
from util.profiler import Profiler
from util.timer import Timer
from util.util_tools import get_source_info
from util.wx_conf import wx_conf


class WX_ConfTest(unittest.TestCase):

    def test_wx_conf_data(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = [0.39, 0.41, 0.51, 0.58, 0.64, 0.64, 0.84, 0.88, 0.97, 1.19,
                2.23, 2.41, 2.44, 2.88, 3.0, 5.4, 7.97, 19.06, 21.85, 39.07]
        med = np.median(data)
        for cf in (.9, .95, .99):
            lc, uc = wx_conf(data, cf)
            print("%7.3f %7.3f %7.3f %7.3f" %
                  (cf, lc, med, uc))

    def test_wx_conf_perf(self):
        print("-- %s(%d): %s --" % get_source_info())
        data_sets = [[weibullvariate(1, .75) for _ in range(25)]
                     for _ in range(300)]
        with Timer() as tm:
            for _ in range(1000):
                wx_conf(choice(data_sets))
        print(tm)

if __name__ == '__main__':
    unittest.main()
