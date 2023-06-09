import unittest
import inspect
from util.data_generator import gen_dates
from util.charts import chart
from util.data_generator import gen_flat
from util.smoothers import (
    des,
    ghf,
    kfs,
    ses,
    sma,
    tes
)
from util.stat_utils import (
    fit,
    mean
)
from util.timer import Timer


DATA1 = [3.39, 2.96, 3.1, 2.86, 3.71, 0.75, 3.62, 0.65, 0.78, 4.91,
         2.35, 1.53, 3.24, 4.47, 2.34, 4.54, 5.64, 5.53, 6.69, 4.54, 5.41,
         5.89, 7.73, 6.13, 8.38, 7.56, 4.18, 9.73, 8.98, 5.32]


DATA2 = [2.77, 4.6, 3.77, 6.04, 3.99, 3.17, 4.02, 4.23, 5.78, 3.6, 3.05,
         3.38, 3.7, 2.6, 3.64, 1.89, 1.73, 1.87, 2.41, 2.85, 1.86, 3.08,
         2.29, 2.56, 2.63, 4.42, 4.19, 2.01, 3.26, 2.16, 3.02, 3.27, 2.23,
         1.73, 2.5, 2.67, 3.24, 1.86, 2.3, 1.94, 1.46, 1.44, 1.15, 1.91,
         1.51, 1.62, 2.73, 4.71, 2.34, 2.03, 2.21, 3.72, 3.04, 3.21, 2.48,
         3.2, 3.53, 2.77, 3.09, 2.65, 3.52, 2.66, 3.01, 1.66, 1.19, 0.93,
         1.96, 1.55, 1.94, 1.73, 1.8, 3.06, 2.6, 2.95, 1.98, 6.13, 3.18,
         4.04, 2.99, 6.56, 4.5, 4.18, 1.69, 2.77, 4.9, 2.51, 3.54, 2.02,
         2.25, 1.62, 1.81, 2.02, 2.24, 3.35, 2.55, 3.91, 3.94, 5.5, 6.19,
         4.2, 5.42, 4.58, 5.92, 3.25, 4.36, 5.55, 3.07, 3.08, 3.85, 2.2,
         3.02, 0.99, 2.02, 1.66, 2.39, 3.21, 2.68, 2.58, 1.0, 4.91]

DATA3 = [3.15, 6.13, 4.78, 5.89, 3.57, 2.83, 2.94, 2.29, 1.37, 2.22, 2.76,
         2.84, 1.64, 2.32, 3.79, 3.12, 3.2, 3.47, 3.4, 4.47, 3.31, 5.01,
         1.99, 5.88, 5.17, 5.56, 5.04, 3.03, 3.67, 2.38, 1.96, 1.23, 1.61,
         1.54, 1.15, 2.24, 2.11, 1.56, 2.9, 1.54, 2.39, 3.26, 1.56, 2.61,
         3.13, 3.04, 2.36, 3.76, 2.74, 3.49, 1.7, 2.24, 2.76, 2.76, 3.02,
         1.56, 1.78, 1.78, 1.8, 1.73, 1.36, 1.34, 2.11, 2.38, 3.69, 3.03,
         2.08, 2.56, 3.01, 3.05, 2.42, 3.43, 3.24, 2.87, 3.65, 4.8, 2.23,
         2.55, 1.88, 2.07, 1.84, 1.48, 1.27, 2.28, 1.57, 2.47, 2.57, 3.6,
         3.08, 5.79, 3.47, 5.12, 3.44, 3.54, 3.46, 3.75, 4.52, 4.45, 4.34,
         3.36, 3.73, 3.99, 1.77, 3.0, 1.81, 2.82, 1.72, 1.85, 1.18, 3.07,
         3.11, 3.55, 3.64, 3.18, 2.74, 5.81, 4.4, 5.36, 4.29, 5.34]


class TestSmoothers(unittest.TestCase):

    def test_level(self):
        print('-- %s --' % inspect.stack()[0][3])
        day_n = 288
        data_n = day_n * 5
        for sfn in (des, ghf, kfs, ses, sma, tes):
            mapes = []
            mpes = []
            with Timer() as tm:
                for i in range(30):
                    dates, obs = gen_flat(1, day_n, data_n, sc=3)
                    eps = list(sfn(obs))
                    if i == 0:
                        chart('level_%s' % sfn.__name__, dates, (obs, eps))
                    mape, mpe = fit(obs, eps)
                    mapes.append(mape)
                    mpes.append(mpe)
            print(sfn.__name__, mean(mapes), mean(mpes), tm)

    def test_trend(self):
        print('-- %s --' % inspect.stack()[0][3])
        day_n = 288
        data_n = day_n * 5
        for sfn in (des, ghf, kfs, ses, sma, tes):
            mapes = []
            mpes = []
            with Timer() as tm:
                for i in range(30):
                    dates, obs = gen_flat(1, day_n, data_n, sc=3, trend_f=.001)
                    eps = list(sfn(obs))
                    if i == 0:
                        chart('trend_%s' % sfn.__name__, dates, (obs, eps))
                    mape, mpe = fit(obs, eps)
                    mapes.append(mape)
                    mpes.append(mpe)
            print(sfn.__name__, mean(mapes), mean(mpes), tm)

    def test_des(self):
        print('-- %s --' % inspect.stack()[0][3])
        obs = DATA1
        eps = list(des(obs, a=.35, b=.02))
        mape, mpe = fit(obs, eps)
        print(mape, mpe)
        chart('des', gen_dates(24, len(obs)), (obs, eps))

    def test_ghf(self):
        print('-- %s --' % inspect.stack()[0][3])
        obs = DATA1
        eps = list(ghf(obs))
        mape, mpe = fit(obs, eps)
        print(mape, mpe)
        chart('ghf', gen_dates(24, len(obs)), (obs, eps))

    def test_kfs(self):
        print('-- %s --' % inspect.stack()[0][3])
        obs = DATA1
        eps = list(kfs(obs))
        mape, mpe = fit(obs, eps)
        print(mape, mpe)
        chart('kfs', gen_dates(24, len(obs)), (obs, eps))

    def test_ses(self):
        print('-- %s --' % inspect.stack()[0][3])
        obs = DATA1
        eps = list(ses(obs, a=.3))
        mape, mpe = fit(obs, eps)
        print(mape, mpe)
        chart('ses', gen_dates(24, len(obs)), (obs, eps))

    def test_sma(self):
        print('-- %s --' % inspect.stack()[0][3])
        obs = DATA3
        eps = list(sma(obs))
        mape, mpe = fit(obs, eps)
        print(mape, mpe)
        chart('sma', gen_dates(24, len(obs)), (obs, eps))


if __name__ == '__main__':
    unittest.main()
