"""
Moving period smoother that estimates expected values from a cyclical or
periodic time-series. Medians are used for estimates and rank sums are
used for tracking scores. This provides robustness for spiky, highly variable
timeseries.
"""
from bisect import bisect_left
from collections import defaultdict, deque
from math import sqrt
import numpy as np
from util.stat_utils import (
    period_key,
    period_truncate,
    periods_per_day
)


def mps(dates, values, win_mins=180, test_mins=60):
    """
    Moving period smoother and tester for timeseries 'dates' and 'values'
    where 'win_mins' is the size of the window thast will be centered around
    the current value. Values are collected for the past three days of the
    same type (weekday or weekend) for the window. The collected values
    for each window are aggregated using median to produce an estimated value.
    Rank sums is used to caslculate a test score comparing the past 'test_mins'
    estimated values to the actual values. Returns estimated values and
    tracking scores for each value.
    """
    # Number of periods to test.
    day_n = periods_per_day(dates)
    test_n = (test_mins * day_n) // 1440
    n = len(dates)
    if n < day_n * 3:
        raise ValueError("No enough data.")

    # Generate period keys for each date, centered withi 'win_mins'.
    periods = [period_key(period_truncate(d, win_mins * 60)) for d in dates]

    # For updating the model.
    estimates = [x for x in values]
    pd_values = defaultdict(deque)

    # For calculating tracking scores.
    stage = []
    base = []
    sl = sh = 0
    a = 2 / (test_n - 1)
    ref_n = int(sqrt(n))
    scores = [0] * n

    for i in range(n):
        if i >= day_n:
            # Load the value into into the assigned period.
            pk = periods[i - day_n]
            pd_values[pk].appendleft(values[i - day_n])
            if len(pd_values[pk]) > test_n * 3:
                pd_values[pk].pop()

        pk = periods[i]
        if pk in pd_values and len(pd_values[pk]) >= 3:
            # Estimate smoothed value.
            estimates[i] = np.median(pd_values[pk])
            dx = values[i] - estimates[i]
            stage.append(dx)
            if len(stage) == ref_n:
                # Refresh base values to test against.
                base.extend(stage)
                base.sort()
                stage = []
            if len(base):
                # Estimate tracking score.
                pr = ((bisect_left(base, dx) / (len(base) - .5)) - .5) * 2
                sl = min((a * pr) + ((1 - a) * sl), 0)
                sh = max((a * pr) + ((1 - a) * sh), 0)
                scores[i] = sh**a if sh > abs(sl) else -(abs(sl)**a)

    return estimates, scores
