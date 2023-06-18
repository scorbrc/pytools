"""
Holt Winters triple exponential for cyclical data. Estimates level, trend
and cycle. See https://otexts.com/fpp2/holt-winters.html. This implementation
differs slightly in that cycles are based on type of day, either weekday or
weekend. This allows capturing weekly and daily cycles with less data.
"""
from collections import defaultdict
from math import sqrt
from util.stat_utils import (
    period_key,
    periods_per_day
)
from util.transform import (
    fr_sqrt_trans,
    to_sqrt_trans
)


def hws(dates, values, fc_n=None, sm_coef=None):
    """
    Holt-Winters exponential smoothing for level, trend and cycle, where cycle
    is based on type of day (weekday/weekend). 'dates' are dates for each period
    'values' has the observed value for each period. 'fc_n' is number of periods
    to forecast forward, defaults to 3 hours. 'sm_coef' are the smoothing
    coefficients for level, trend, cycle and dampling. All must be (0 < sc < 1).
    Returns estimated values and normalized tracking scores.
    """
    # Determine how many periods per day.
    day_n = periods_per_day(dates)
    n = len(values)
    if n < day_n * 3:
        raise ValueError("Not enough data.")

    # Create a key for each period.
    pks = [period_key(d) for d in dates]
    obs = to_sqrt_trans(values)
    eps = [x for x in obs]
    scs = [0] * n

    if fc_n is None:
        # Default forecast forward to three hours.
        fc_n = day_n // 8

    if sm_coef is not None:
        # Validate level, trend, season and damper smoothing coefficients.
        if len(sm_coef) != 4 or min(sm_coef) <= 0 or max(sm_coef) >= 1:
            raise ValueError(
                "Expected level, trend, season and damper: 0 < sc < 1.")
        a, b, g, d = sm_coef
    else:
        # Default level, trend, season and damper smoothing coefficients.
        a = 2 / (day_n / 12 - 1)
        b = 2 / (n / 2 - 1)
        g = (day_n * 2) / (n - 1)
        d = 1 - (1 / sqrt(day_n))

    # Initialize the model with level, trend and cycle.
    u1 = wd = sum(obs) / n
    b1 = sum([obs[i] - obs[i - 1] for i in range(n)]) / (n - 1)
    ss = defaultdict(list)
    for pk, x in zip(pks, obs):
        ss[pk].append(x)
    for pk in ss:
        ss[pk] = sum(ss[pk]) / len(ss[pk])

    # Run the model, updating for each value and forecasting 'fc_n' periods.
    sl = sh = 0
    wd = 1
    gp = sqrt(a / (2 - a)) * 2
    for t in range(0, n):
        # Use the difference between observed and forecasted value.
        dx = obs[t] - eps[t]
        if t >= day_n:
            # Update variation, front-loading the smoothing.
            f = max(2 / (t - day_n + 2), b)
            wd = (f * abs(dx)) + ((1 - f) * wd)
            if wd > 0:
                # Update the tracking score.
                ts = dx / (wd * 2)
                sl = min((a * ts) + ((1 - a) * sl), 0)
                sh = max((a * ts) + ((1 - a) * sh), 0)
                scs[t] = max(sl, sh, key=abs) / gp

        if t < n - fc_n:
            # Update the level, trend and cycle, estimate 'fc_n' periods ahead.
            u0 = u1
            b0 = b1 * d
            u1 = (a * (obs[t] - ss[pks[t]])) + ((1 - a) * (u0 + b0))
            b1 = (b * (u1 - u0)) + ((1 - b) * b0)
            ss[pks[t]] = (g * (obs[t] - u0 - b0)) + ((1 - g) * ss[pks[t]])
            eps[t + fc_n] = max(u1 + (b1 * fc_n) + ss[pks[t + fc_n]], 0)

    return fr_sqrt_trans(eps), scs
