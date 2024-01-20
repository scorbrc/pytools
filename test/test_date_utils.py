import unittest
from datetime import datetime, timedelta
from util.date_utils import (
    days_from_month,
    work_week
)
from util.time_utils import to_utc
from util.util_tools import get_source_info


class DateUtilsTest(unittest.TestCase):

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

    def test_work_week(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(0, work_week(datetime(2020, 1, 1))[1])
        self.assertEqual(3, work_week(datetime(2020, 1, 1))[2].day)
        self.assertEqual(3, work_week(datetime(2020, 1, 3))[2].day)
        self.assertEqual(1, work_week(datetime(2020, 1, 4))[1])
        self.assertEqual(10, work_week(datetime(2020, 1, 4))[2].day)
        self.assertEqual(4, work_week(datetime(2020, 1, 31))[1])
        self.assertEqual(31, work_week(datetime(2020, 1, 31))[2].day)
        self.assertEqual(5, work_week(datetime(2020, 2, 1))[1])
        self.assertEqual(7, work_week(datetime(2020, 2, 1))[2].day)


if __name__ == '__main__':
    unittest.main()
