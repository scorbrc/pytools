import unittest
from random import choice, choices, randint, weibullvariate
from string import ascii_uppercase
from uuid import uuid4
from util.describer import describe
from util.fld_char import Field, FieldChars
from util.random_utils import RandomUtils
from util.stat_utils import fit
from util.util_tools import get_source_info


DATA = [0.52, 0.55, 0.56, 0.63, 0.64, 0.65, 0.66, 0.72, 0.75, 0.75, 0.79, 0.8, 0.89, 0.91, 0.92, 0.93, 0.95, 0.96, 0.96, 0.98, 0.99, 1.01, 1.03, 1.05, 1.06, 1.06, 1.1, 1.1, 1.11, 1.12, 1.12, 1.15, 1.16, 1.25, 1.31, 1.32, 1.37, 1.44, 1.44, 1.46, 1.49, 1.49, 1.52, 1.55, 1.55, 1.64, 1.65, 1.7, 1.72, 1.76, 1.77, 1.81, 1.83, 1.9, 1.9, 1.99, 2.02, 2.03, 2.03, 2.15, 2.16, 2.2, 2.26, 2.3, 2.31, 2.33, 2.35, 2.35, 2.36, 2.37, 2.38, 2.44, 2.44, 2.55, 2.55, 2.57, 2.57, 2.57, 2.6, 2.6, 2.6, 2.62, 2.62, 2.63, 2.64, 2.67, 2.67, 2.68, 2.75, 2.76, 2.81, 2.83, 2.85, 2.85, 2.91, 2.91, 2.93, 2.99, 3.01, 3.01, 3.07, 3.12, 3.12, 3.13, 3.13, 3.26, 3.27, 3.31, 3.33, 3.38, 3.45, 3.47, 3.5, 3.58, 3.59, 3.6, 3.62, 3.63, 3.7, 3.73, 3.73, 3.75, 3.77, 3.83, 3.89, 3.92, 3.99, 4.0, 4.04, 4.11, 4.14, 4.17, 4.28, 4.32, 4.35, 4.37, 4.45, 4.47, 4.54, 4.61, 4.63, 4.72, 4.76, 4.94, 5.03, 5.06, 5.08, 5.08, 5.14, 5.34, 5.41, 5.43, 5.48, 5.62, 5.74, 5.77, 5.81, 5.83, 5.87, 5.91, 5.95, 6.01, 6.02, 6.13, 6.18, 6.26, 6.37, 6.39, 6.42, 6.42, 6.44, 6.65, 6.65, 6.81, 6.84, 6.85, 6.91, 7.22, 7.3, 7.59, 7.79, 8.07, 8.16, 8.32, 8.38, 8.4, 8.52, 8.66, 8.76, 9.54, 9.55, 9.7, 9.95, 10.22, 10.44, 10.76, 11.0, 12.5, 13.31, 16.84]

class FldCharTest(unittest.TestCase):

    def test_field_code(self):
        print("-- %s(%d): %s --" % get_source_info())
        fld = Field('code')
        for _ in range(30):
            x = ''.join(choices(ascii_uppercase, k=randint(4, 8)))
            for _ in range(max(int(weibullvariate(10, .5)), 1)):
                fld.count(x)
        print(fld)
        for x, p in fld.probs():
            print("%-15s %.4f" % (x, p))

    def test_field_number(self):
        print("-- %s(%d): %s --" % get_source_info())
        fld = Field('fldnum')
        for x in DATA:
            fld.count(x)
        print(fld)
        print(fld.describe())
        print()
        ds = fld.fit()
        if ds is not None:
            base = [v for k, v in ds.data_ds.items() if k not in ('name', 'n')]
            test = [v for k, v in ds.fitted_ds.items() if k not in ('name', 'n')]
            mape, mpe = fit(base, test)
            self.assertTrue(abs(mpe) < 10)
            self.assertTrue(mape < 30)
            test_ds = describe(ds.gen_data(200), 'test', full_pcts=True)
            test = [ v for k, v in test_ds.items() if k not in ('name', 'n')]
            mape, mpe = fit(base, test)
            self.assertTrue(abs(mpe) < 15)
            self.assertTrue(mape < 30)


    def test_records(self):
        print("-- %s(%d): %s --" % get_source_info())
        records = []
        rn = RandomUtils()
        for i in range(10):
            records.append(
                dict(
                    id=rn.short_uid(),
                    seq=i,
                    date=rn.date(),
                    amt=rn.random().weibullvariate(5, .75),
                    cd1=rn.digits(1),
                    fld1=rn.b62(20)
                )
            )
        fc = FieldChars.evaluate(records)
        print(fc.report())



if __name__ == '__main__':
    unittest.main()
