"""
A/B testing for comparing last so many after test values to a matching set of
before values.
"""
import datetime as dt
from util.open_record import OpenRecord
from util.stat_utils import fit
from util.stat_utils import median
from util.stat_utils import pct_diff
from util.stat_utils import period_key
from util.stat_utils import periods_per_day
from util.stat_utils import rs_test
from util.util_tools import zero_if_none


def ab_test(name,
            dates,
            values,
            test_n=15,
            day_type_n=3,
            hour_n=3,
            lower_h=-3,
            upper_h=3,
            min_pcd=15):
    """
    After/Before period tester that compares the last 'test_n' periods from
    time-series 'dates' and 'values' to a set of before periods that match the
    set of after periods. A period is the minute, hour, and type of day, either
    weekday or weekend.
    'name' just a name given to the test result returned.
    'test_n' is the last so many after values to test.
    'day_type_n' is the number days of the same type to select.
    'hour_n' is the number of hours to select.
    If there are enough periods then before periods selected will be
    test_n * day_type_n * hour_n
    'lower_h' is the lower threshold for failure indicating after values
    are less than before values.
    'upper_h' is the lower threshold for failure indicating after values
    are greater than before values.
    'min_pcd' is minimum percentage difference between before and
    after values before accepting a test failure.
    """
    data_set = OpenRecord(name=name)
    test = OpenRecord(
        name=name,
        periods=len(dates),
        test_n=test_n,
        day_type_n=day_type_n,
        hour_n=hour_n,
        lower_h=-lower_h,
        upper_h=upper_h,
        score=0,
        min_pcd=min_pcd,
        is_under=False,
        is_over=False
    )
    # Make sure test has enough data.
    if len(dates) > day_type_n * hour_n * test_n:
        day_n = periods_per_day(dates)
        if len(dates) > day_n * 3:

            # Select the after value periods.
            data_set.a_dates = dates[-test_n:]
            data_set.a_values = zero_if_none(values[-test_n:])
            a_periods = set()
            for date in data_set.a_dates:
                # Add an hour period for the exact date.
                a_periods.add(period_key(date))
                if hour_n > 1:
                    # Allocate additional hours.
                    n = (hour_n - 1) // 2
                    m = (hour_n - 1) % 2
                    for i in range(n + m):
                        a_periods.add(
                            period_key(date - dt.timedelta(hours=i + 1)))
                    for i in range(n):
                        a_periods.add(
                            period_key(date + dt.timedelta(hours=i + 1)))

            # Find periods that match the set of after periods, starting one
            # day back. Stop if maximum possible periods reached.
            data_set.b_dates = []
            data_set.b_values = []
            max_possible = test_n * hour_n * day_type_n
            for i in range(len(dates) - day_n, -1, -1):
                pd = period_key(dates[i])
                if pd in a_periods:
                    data_set.b_dates.append(dates[i])
                    data_set.b_values.append(zero_if_none(values[i]))
                    if len(data_set.b_values) >= max_possible:
                        break

            # Test after values against before values.
            test.before = median(data_set.b_values)
            test.after = median(data_set.a_values)
            test.mape, test.mpe = fit(data_set.b_values, test.before)
            test.pct_diff = pct_diff(test.after, test.before)
            test.score = rs_test(data_set.b_values, data_set.a_values)
            test.is_under = False
            test.is_over = False
            if abs(test.pct_diff) > min_pcd:
                if test.score < lower_h:
                    test.is_under = True
                if test.score > upper_h:
                    test.is_over = True

    return test, data_set
