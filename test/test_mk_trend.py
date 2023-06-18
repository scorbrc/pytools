import unittest
from util.data_generator import gen_flat
from util.open_record import OpenRecord
from util.mk_trend import mk_trend
from util.stat_utils import describe
from util.timer import Timer
from util.util_tools import get_source_info


DATA1 = [14.34, 15.27, 2.64, 11.6, 28.81, 35.01, 24.5, 25.78, 11.94, 13.95,
         22.84, 21.67, 32.45, 8.96, 15.38, 32.34, 41.75, 4.87, 4.89, 30.59,
         36.24, 10.6, 38.55, 15.29, 27.17, 28.55, 16.9, 39.67, 18.93, 22.21,
         27.81, 35.98, 41.43, 39.02]

DATA2 = [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 2, 1, 2, 2]

DATA3 = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1,
         2, 5, 1, 2, 2, 2, 0, 5, 2, 2, 3, 4, 5, 1, 4, 1, 0, 5, 3, 4, 1,
         0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0]


class TestMKTrend(unittest.TestCase):

    def test_mk_trend_values(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = [x for x in DATA1]
        self.assertEqual(2.46, round(mk_trend(data), 2))
        data.reverse()
        self.assertEqual(-2.46, round(mk_trend(data), 2))

    def test_mk_trend_values_flat(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(0, mk_trend([1] * 20))

    def test_mk_trend_counts(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(3.52, round(mk_trend(DATA2), 2))

    def test_mk_trend_middle(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(.33, round(mk_trend(DATA3), 2))
        self.assertEqual(4.63, round(mk_trend(DATA3[:40]), 2))

    def test_mk_trend_range(self):
        print("-- %s(%d): %s --" % get_source_info())
        names = []
        dss = []
        for n in (50, 100, 200):
            tss = []
            for _ in range(100):
                data, _ = gen_flat(1, 288, n, trend_f=.001)
                tss.append(mk_trend(data))
            dss.append(describe(tss))
            names.append(str(n))
        rpt = OpenRecord.to_text_cols(dss)
        self.assertTrue(dss[1].mu > dss[0].mu, rpt)
        self.assertTrue(dss[2].mu > dss[1].mu, rpt)

    def test_mk_trend_large(self):
        print("-- %s(%d): %s --" % get_source_info())
        with Timer() as tm:
            _, data = gen_flat(1, 288, 2000, trend_f=.005)
            mk_trend(data)
        self.assertTrue(tm.secs < .2)


if __name__ == '__main__':
    unittest.main()
