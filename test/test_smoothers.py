import unittest
from util.data_generator import gen_dates
from util.charts import chart
from util.data_generator import gen_flat
from util.smoothers import (
    des,
    ghf,
    kfs,
    ses,
    sma
)
from util.stat_utils import (
    fit,
    mean
)
from util.timer import Timer
from util.util_tools import get_source_info


class TestSmoothers(unittest.TestCase):

    def test_level(self):
        print("-- %s(%d): %s --" % get_source_info())
        day_n = 288
        data_n = day_n * 5
        for sfn in (des, ghf, kfs, ses, sma):
            mapes = []
            mpes = []
            for i in range(100):
                dates, obs = gen_flat(1, day_n, data_n, sc=3)
                eps = list(sfn(obs))
                if i == 0:
                    chart('level_%s' % sfn.__name__, dates, (obs, eps))
                mape, mpe = fit(obs, eps)
                mapes.append(mape)
                mpes.append(mpe)
            mpe = mean(mpes)
            mape = mean(mapes)
            self.assertTrue(
                abs(mpe) < 10,
                "Expected %s mpe < 5: %.3f" % (sfn.__name__, mpe))
            self.assertTrue(
                abs(mape) < 30,
                "Expected %s mape < 30: %.3f" % (sfn.__name__, mape))

    def test_trend(self):
        print("-- %s(%d): %s --" % get_source_info())
        day_n = 288
        data_n = day_n * 5
        for sfn in (des, ghf, kfs, ses, sma):
            mapes = []
            mpes = []
            with Timer() as tm:
                for i in range(100):
                    dates, obs = gen_flat(1, day_n, data_n, sc=3, trend_f=.001)
                    eps = list(sfn(obs))
                    if i == 0:
                        chart('trend_%s' % sfn.__name__, dates, (obs, eps))
                    mape, mpe = fit(obs, eps)
                    mapes.append(mape)
                    mpes.append(mpe)
            mpe = mean(mpes)
            mape = mean(mapes)
            self.assertTrue(
                abs(mpe) < 15,
                "Expected %s mpe < 5: %.3f" % (sfn.__name__, mpe))
            self.assertTrue(
                abs(mape) < 50,
                "Expected %s mape < 30: %.3f" % (sfn.__name__, mape))


if __name__ == '__main__':
    unittest.main()
