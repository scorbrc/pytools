import unittest
import datetime as dt
from dateutil import tz
from random import randint
from util.time_utils import (
    days_from_month,
    is_local,
    is_tz_aware,
    is_utc,
    last_day_in_week,
    to_local,
    to_utc,
    truncate_to_day,
    truncate_to_hour,
    truncate_to_minute,
    truncate_to_second
)
from util.util_tools import get_source_info


class TimeUtilsTest(unittest.TestCase):

    def test_days_from_month(self):
        print("-- %s(%d): %s --" % get_source_info())
        sdt, edt = days_from_month(to_utc('2014-04-01'))
        self.assertEqual(0, sdt)
        self.assertEqual(30, edt)
        sdt, edt = days_from_month(to_utc('2014-04-02'))
        self.assertEqual(1, sdt)
        self.assertEqual(29, edt)
        sdt, edt = days_from_month(to_utc('2014-04-30'))
        self.assertEqual(29, sdt)
        self.assertEqual(1, edt)

    def test_examples(self):
        print("-- %s(%d): %s --" % get_source_info())
        dt.datetime.now()
        adt = tz.tzoffset('ADT', 10800)
        ast = tz.tzoffset('AST', 14400)
        self.assertEqual(
            '2010-06-01 12:00:00+00:00',
            str(to_utc(dt.datetime(2010, 6, 1, 12))))
        self.assertEqual(
            '2010-06-01 09:00:00+00:00',
            str(to_utc(dt.datetime(2010, 6, 1, 12, tzinfo=adt))))
        self.assertEqual(
            '2010-02-15 08:00:00+00:00',
            str(to_utc(dt.datetime(2010, 2, 15, 12, tzinfo=ast))))
        self.assertEqual(
            '2010-06-01 05:00:00-04:00',
            str(to_local(dt.datetime(2010, 6, 1, 12, tzinfo=adt))))
        self.assertEqual(
            '2010-02-15 03:00:00-05:00',
            str(to_local(dt.datetime(2010, 2, 15, 12, tzinfo=ast))))
        self.assertEqual(
            '2010-06-01 12:00:00+00:00',
            str(to_utc('2010-06-01T12:00:00')))
        self.assertEqual(
            '2010-06-01 21:00:00+00:00',
            str(to_utc('2010-06-01T12:00:00 HDT')))
        self.assertEqual(
            '2010-02-15 22:00:00+00:00',
            str(to_utc('2010-02-15T12:00:00 HST')))
        self.assertEqual(
            '2010-06-01 17:00:00-04:00',
            str(to_local('2010-06-01T12:00:00 HDT')))
        self.assertEqual(
            '2010-02-15 17:00:00-05:00',
            str(to_local('2010-02-15T12:00:00 HST')))

    def test_last_day_in_week(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(
            '2023-04-30', last_day_in_week('2023-04-27').strftime('%Y-%m-%d'))

    def test_to_local(self):
        print("-- %s(%d): %s --" % get_source_info())
        d1 = to_local()
        self.assertTrue(is_tz_aware(d1))
        d2 = dt.datetime.now()
        self.assertFalse(is_tz_aware(d2))
        d3 = to_local(d2)
        self.assertTrue(is_tz_aware(d1))
        self.assertEqual(d2.hour, d3.hour)
        d4 = to_utc()
        d5 = to_local(d4)
        self.assertNotEqual(d4.hour, d5.hour)
        d6 = to_local('%d-06-11T12:00:00' % dt.datetime.now().year)
        self.assertTrue(is_tz_aware(d6), str(d6))
        self.assertTrue(is_local(d6), str(d6))
        d7 = to_local('%d-06-11T12:00:00 HDT' % dt.datetime.now().year)
        self.assertEqual(17, d7.hour)

    def test_to_local_many(self):
        print("-- %s(%d): %s --" % get_source_info())
        edt = dt.datetime.now()
        cdt = edt - dt.timedelta(days=365)
        while cdt < edt:
            d1 = to_local(cdt)
            self.assertEqual(cdt.hour, d1.hour)
            self.assertEqual(cdt.minute, d1.minute)
            self.assertEqual(cdt.second, d1.second)
            cdt += dt.timedelta(days=randint(1, 15))

    def test_to_utc(self):
        print("-- %s(%d): %s --" % get_source_info())
        d1 = to_utc()
        self.assertTrue(is_tz_aware(d1))
        d2 = dt.datetime.utcnow()
        self.assertFalse(is_tz_aware(d2))
        d3 = to_utc(d2)
        self.assertTrue(is_tz_aware(d1))
        self.assertEqual(d2.hour, d3.hour)
        d4 = to_local()
        d5 = to_utc(d4)
        self.assertNotEqual(d4.hour, d5.hour)
        d6 = to_utc('2021-11-11T12:00:00')
        self.assertTrue(is_tz_aware(d6), str(d6))
        self.assertTrue(is_utc(d6), str(d6))
        d7 = to_utc('2022/09/09 07:32 PDT')
        self.assertTrue(is_tz_aware(d7), str(d7))
        self.assertTrue(is_utc(d7), str(d7))
        hr = (d7 - to_utc('2022/09/09 07:32')).total_seconds() / (60 * 60)
        self.assertEqual(7, hr)
        d8 = to_utc('%d/11/09 12:00 EST' % dt.datetime.now().year)
        self.assertEqual(17, d8.hour)

    def test_to_utc_many(self):
        print("-- %s(%d): %s --" % get_source_info())
        edt = dt.datetime.utcnow()
        cdt = edt - dt.timedelta(days=365)
        while cdt < edt:
            d1 = to_utc(cdt)
            self.assertEqual(cdt.hour, d1.hour)
            self.assertEqual(cdt.minute, d1.minute)
            self.assertEqual(cdt.second, d1.second)
            cdt += dt.timedelta(days=randint(1, 15))

    def test_truncate_day(self):
        print("-- %s(%d): %s --" % get_source_info())
        d = truncate_to_day(to_local('2020-02-22T13:17:19'))
        self.assertEqual(0, d.hour)
        self.assertEqual(22, d.day)

    def test_truncate_hour(self):
        print("-- %s(%d): %s --" % get_source_info())
        d = truncate_to_hour(to_local('2020-02-22T13:17:19'))
        self.assertEqual(13, d.hour)
        self.assertEqual(0, d.minute)

    def test_truncate_minute(self):
        print("-- %s(%d): %s --" % get_source_info())
        d = truncate_to_minute(to_local('2020-02-22T13:17:19'))
        self.assertEqual(0, d.second)
        self.assertEqual(17, d.minute)

    def test_truncate_second(self):
        print("-- %s(%d): %s --" % get_source_info())
        d = truncate_to_second(to_utc('2020-02-22T13:17:19.123'))
        self.assertEqual(0, d.microsecond)


if __name__ == '__main__':
    unittest.main()
