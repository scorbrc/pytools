import unittest
from util.describer import Describer, describe
from util.open_record import OpenRecord
from util.util_tools import get_source_info


DATA1 = [14.34, 15.27, 2.64, 11.6, 28.81, 35.01, 24.5, 25.78, 11.94, 13.95,
         22.84, 21.67, 32.45, 8.96, 15.38, 32.34, 41.75, 4.87, 4.89, 30.59,
         36.24, 10.6, 38.55, 15.29, 27.17, 28.55, 16.9, 39.67, 18.93, 22.21,
         27.81, 35.98, 41.43, 39.02]


class TestDescriber(unittest.TestCase):

    def test_describe_rolling(self):
        print("-- %s(%d): %s --" % get_source_info())
        desc = Describer('test', 30)
        for i in range(30):
            desc.add(i)
        ds = desc.describe()
        self.assertEqual(30, ds.n, ds)
        self.assertEqual(14.5, ds.mu, ds)
        self.assertEqual(0, desc.values()[0])
        self.assertEqual(29, desc.values()[-1])
        for i in range(30, 45):
            desc.add(i)
        ds = desc.describe()
        self.assertEqual(30, ds.n, ds)
        self.assertEqual(29.5, ds.mu, ds)
        self.assertEqual(15, desc.values()[0])
        self.assertEqual(44, desc.values()[-1])

    def test_describe_half(self):
        print("-- %s(%d): %s --" % get_source_info())
        ds = describe(DATA1, full_pcts=False)
        for name, value in (('n', 34),
                            ('mu', 23.469),
                            ('sd', 11.497),
                            ('p50', 23.67),
                            ('p75', 32.4225),
                            ('p90', 38.879),
                            ('p95', 40.286),
                            ('p99', 41.644),
                            ('p995', 41.697),
                            ('p999', 41.739),
                            ('p100', 41.75)):
            self.assertAlmostEqual(value, ds[name], 3, ds)

    def test_describe_full(self):
        print("-- %s(%d): %s --" % get_source_info())
        data = list(range(300))
        ds = describe(data, full_pcts=True)
        for name, value in (('n', 300.0),
                            ('mu', 149.5),
                            ('sd', 86.747),
                            ('p00', 0.0),
                            ('p001', .299),
                            ('p005', 1.495),
                            ('p01', 2.99),
                            ('p05', 14.950),
                            ('p10', 29.900),
                            ('p25', 74.75),
                            ('p50', 149.5),
                            ('p75', 224.25),
                            ('p90', 269.1),
                            ('p95', 284.05),
                            ('p99', 296.01),
                            ('p995', 297.505),
                            ('p999', 298.701),
                            ('p100', 299)):
            self.assertAlmostEqual(value, ds[name], 3, ds)
        content = OpenRecord.to_text_cols(ds)
        self.assertEqual(19, len(content.split('\n')), content)


if __name__ == '__main__':
    unittest.main()
