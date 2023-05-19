from bisect import bisect_left
from collections import defaultdict
from math import sqrt
from util.stat_utils import (
    median,
    period_key,
    period_truncate,
    periods_per_day,
    rs_test
)


def mps(dates, values, win_mins=180, test_mins=60, agg_fn=median, test_fn=rs_test):
    """
    Moving window smoother and tester for timeseries 'dates' and 'values'
    where 'win_mins' is the size of the window thast will be centered around
    the current value. Values are collected for the past three days of the
    same type (weekday or weekend) for the window. The collected values
    for each window are aggregated using 'agg_fn' (median, mean) to produce
    an estiamted value. Function 'test_fn' (rs_test, ti_test) is used to test
    the past 'test_mins' estiamted values to the actual value to calculate a
    tracking score. Returns estimated values and tracking scores for each value.
    """
    # Number of periods to test.
    day_n = periods_per_day(dates)
    test_n = (test_mins * day_n) // 1440

    # Period keys for each date.
    periods = [period_key(period_truncate(d, win_mins * 60)) for d in dates]

    estimates = [x for x in values]
    scores = [0] * len(dates)
    pd_values = defaultdict(list)

    for i in range(len(dates)):
        if i >= day_n:
            # Load the value into into the assigned period.
            pk = periods[i - day_n]
            pd_values[pk].append(values[i - day_n])
            if len(pd_values[pk]) > test_n * 3:
                pd_values[pk].pop(0)

        pk = periods[i]
        if pk in pd_values and len(pd_values[pk]) >= 3:
            # Estimate smoothed value and test score.
            estimates[i] = median(pd_values[pk])
            scores[i] = rs_test(pd_values[pk], values[i - test_n + 1:i + 1])

    return estimates, scores
