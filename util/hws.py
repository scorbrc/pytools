"""
Holt Winters triple exponential for cyclical data. Estimates level, trend
and cycle, where cycle is based on type of day, either weekday or weekend.
See https://otexts.com/fpp2/holt-winters.html for a general explanation.
"""
from collections import defaultdict, deque
from math import sqrt
from util.stat_utils import (
    period_key,
    periods_per_day
)
from util.transform import (
    fr_sqrt_trans,
    to_sqrt_trans
)

def xhws(dates, values):
    """
    Holt Winters triple exponential smoothing for lever, trend and day type
    (weekday or weekend), where 'dates' and 'values' are the timeseries
    periods, Returns estimated values and normalized tracking scores.
    """
    # Determine number of periods in a day.
    day_n = periods_per_day(dates)
    n = len(values)
    if n < day_n * 3:
        raise ValueError("Not enough data.")

    pks = [period_key(d) for d in dates]
    obs = to_sqrt_trans(values)
    eps = [x for x in obs]
    scs = [0] * n

    # Default forecast forward to three hours.
    fc_n = day_n // 8

    # Default level, trend, season and damper smoothing coefficients.
    a = 1 / sqrt(day_n)
    b = 1 / sqrt(n)
    g = (day_n * 2) / (n - 1)
    d = 1 - (1 / sqrt(day_n))

    # Initialize the model with level, trend and cycle.
    u1 = wd = wu = sum(obs) / n
    b1 = sum([obs[i] - obs[i - 1] for i in range(n)]) / (n - 1)
    ss = defaultdict(list)
    for pk, x in zip(pks, obs):
        ss[pk].append(x)
    for pk in ss:
        ss[pk] = sum(ss[pk]) / len(ss[pk])

    # Run the model.
    sl = sh = 0
    for t in range(0, n):

        if t >= day_n * 3:
            # Estimate tracking score.
            dx = obs[t] - eps[t]
            wd = (b * abs(dx)) + ((1 - b) * wd)
            wu = (b * dx) + ((1 - b) * wu)
            ts = wu / (wd * sqrt(a / (2 - a)))
            sl = min((a * ts) + ((1 - a) * sl), 0)
            sh = max((a * ts) + ((1 - a) * sh), 0)
            scs[t] = max(sl, sh, key=abs)

        if t < n - fc_n:
            # Update the model asnd estimate value 'fc_n' periods ahead.
            u0 = u1
            b0 = b1 * d
            u1 = (a * (obs[t] - ss[pks[t]])) + ((1 - a) * (u0 + b0))
            b1 = (b * (u1 - u0)) + ((1 - b) * b0)
            ss[pks[t]] = (g * (obs[t] - u0 - b0)) + ((1 - g) * ss[pks[t]])
            eps[t + fc_n] = max(u1 + (b1 * fc_n) + ss[pks[t + fc_n]], 0)

    return fr_sqrt_trans(eps), scs


def ewma(data, a=.2, b=.01):
    wu = wd = 1
    sl = sh = 0
    for i, x in enumerate(data):
        wd = smooth(i, b, abs(x - wu), wd)
        wu = smooth(i, b, x, wu)
        ts = wu / (wd * sqrt(a / (2 - a)))
        sl = min((a * ts) + ((1 - a) * sl), 0)
        sh = max((a * ts) + ((1 - a) * sh), 0)
        yield max(sl, sh, key=abs)

def smooth(i, f, x, y):
    """
    Exponentially smooth 'x', where 'i' is the period index, 'f' is the
    smoothing coefficient and 'y' is the last smoothed value.
    """
    a = max(2 / (i + 2), f)
    return (a * x) + ((1 - a) * y)


def hws(dates, data):

    n = len(data)
    pks = [period_key(d) for d in dates]
    day_n = periods_per_day(dates)
    fc_n = day_n // 8

    a = 1 / sqrt(day_n)
    b = 1 / sqrt(n)
    g = (day_n * 2) / (n - 1)
    d = 1 - (1 / sqrt(day_n))

    u1 = b1 = 1
    ss = {}
    for pk in pks:
        ss[pk] = 1

    wu = wd = 1
    sl = sh = 0

    ys = deque([0] * fc_n)
    for i, x in enumerate(data):

        ts = 0
        y = x
        if i >= day_n:
            dx = x - ys[-1]
            wd = smooth(i, b, abs(dx), wd)
            wu = smooth(i, b, dx, wu)
            tx = wu / (wd * sqrt(a / (2 - a)))
            sl = min((a * tx) + ((1 - a) * sl), 0)
            sh = max((a * tx) + ((1 - a) * sh), 0)
            ts = max(sl, sh, key=abs)
            y = ys[-1]

        if i < n - fc_n:
            u0 = u1
            b0 = b1 * d
            u1 = smooth(i, a, x - ss[pks[i]], u0 + b0)
            b1 = smooth(i, b, u1 - u0, b1)
            ss[pks[i]] = smooth(i // day_n, g, x - u0 - b0, ss[pks[i]])
            ys.popleft()
            ys.append(max(u1 + (b1 * fc_n) + ss[pks[i + fc_n]], 0))

        yield y, ts
