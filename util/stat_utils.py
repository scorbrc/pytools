"""
Statistical utility functions.
"""
from collections import defaultdict
import datetime as dt
from math import ceil, copysign, exp, floor, sqrt
import numpy as np
from .util_tools import zero_if_none


def adjust_mean(data, mu, prec=.01):
    """ Adjust values in 'data' to mean 'mu' with precision 'prec'. """
    adj_data = [x for x in data]
    for i in range(30):
        m1 = np.mean(adj_data)
        df = mu - m1
        pd = abs(df / ((mu + m1) / 2))
        if pd <= prec:
            break
        adj_data = [x + df for x in adj_data]
    return adj_data


def arl(k, h):
    return ceil((exp(-2 * k * (h + 1.166)) +
                (2 * k * (h + 1.166)) - 1) / (2 * k**2))


def c4(n):
    """ Correction for small sample sizes as used in control charting. """
    return (4 * max(n, 2) - 4) / (4 * max(n, 2) - 3)


def describe(values, pcts=(1, 5, 10, 25, 50, 75, 90, 95, 99)):
    """
    Descriptive statistics for 'values':
      n: number of values
      mu: arithmetic mean
      sd: sample standard deviation
      kr: kurtosis as a measure of distribution
      min: minimum Value
      p01..p99: percentiles as defined in 'pcts'
      max: maximum value
    """
    n = len(values)
    if n < 3:
        raise ValueError("Need at least three values.")
    xs = sorted(values)
    desc = dict(n=n, mu=sum(values) / n, sd=0, kr=0, min=xs[0])
    ks = ss = 0
    for x in xs:
        dx = x - desc['mu']
        ks += dx ** 4
        ss += dx ** 2
    if ss > 0:
        desc['sd'] = sqrt(ss / (n - 1))
    if ks > 0 and desc['sd'] > 0:
        desc['kr'] = (ks / ((desc['sd'] ** 4) * (n - 1))) - 3
    for pct in sorted(pcts):
        r = ((n - 1) * (float(pct) / 100))
        i = int(r)
        pv = xs[i]
        if i < n and r - i > 0:
            pv = xs[i] + ((xs[i + 1] - xs[i]) * (r - i))
        desc['p%02d' % pct] = pv
    desc['max'] = xs[-1]
    return desc


def fit(obs, eps):
    """
    Measure the fit between observed 'obs' and expected 'eps' values
    returning mean absolute percentage error and mean percentage error.
    """
    if len(obs) < 2:
        return 0, 0
    mape = mpe = 0
    if not isinstance(eps, (list, tuple)):
        eps = [eps] * len(obs)
    try:
        for x, y in zip(obs, eps):
            pcd = pct_diff(x, y)
            mape += abs(pcd)
            mpe += pcd
    except FloatingPointError:
        pass
    return mape / len(obs), mpe / len(obs)


def mk_trend(data):
    """
    Mann-Kendall trend test for 'data', which should be a time-series.
    Compares before/after ranks for each value, generating a normalized
    test score adjusted for any tied groups of values. See
    https://vsp.pnnl.gov/help/Vsample/Design_Trend_Mann_Kendall.htm.
    """
    score = 0
    n = len(data)
    if n >= 12:
        tg = 0
        vc = defaultdict(int)
        for x in data:
            vc[x] += 1
        if len(vc) > 1:
            for c in vc.values():
                tg += (c * (c - 1)) * ((2 * c) + 5)
            sd = (((n * (n - 1) * (2 * n + 5)) - tg) / 18)**(1 / 2)
            if sd > 0:
                rs = 0
                for i, y in enumerate(data[:-1]):
                    for x in data[i + 1:]:
                        if x < y:
                            rs -= 1
                        elif x > y:
                            rs += 1
                score = (rs - copysign(1, rs)) / sd
    return score


def pct_diff(x, y):
    """
    Percentage difference between 'x' and 'y' calculated equidistant
    from each other. Returns -200 <= pd <= 200.
    """
    return (x - y) / ((x + y) / 2) * 100 if x + y != 0 else 0


def p50(data):
    """ The 50th peercentile value in 'data'. """
    return np.percentile(data, 50)


def p90(data):
    """ The 90th peercentile value in 'data'. """
    return np.percentile(data, 90)


def p95(data):
    """ The 95th peercentile value in 'data'. """
    return np.percentile(data, 95)


def p99(data):
    """ The 99th peercentile value in 'data'. """
    return np.percentile(data, 99)


def period_key(date):
    """
    Generates a period key from 'date' as HH:MM:WD|WE where
    'WD'=weekday and 'WE'=weekend.
    """
    if date.weekday() < 5:
        return "WD:%02d:%02d" % (date.hour, date.minute)
    return "WE:%02d:%02d" % (date.hour, date.minute)


def period_truncate(date, secs):
    """ Truncates 'date' to 'secs'. """
    epoch_secs = ((date.timestamp() // secs) * secs) + (secs // 2)
    return dt.datetime.fromtimestamp(epoch_secs)


def periods_per_day(dates):
    """ Determines how many periods per day for 'dates'. """
    return int((60 * 60 * 24) // period_secs(dates))


def period_secs(dates):
    """ Determines how many seconds are in the periods for 'dates'. """
    psecs = 2**31 - 1
    for i in range(1, len(dates)):
        secs = (dates[i] - dates[i - 1]).seconds
        if secs > 0 and secs < psecs:
            psecs = secs
    return psecs


def rankdata(data):
    """
    Ranks values in 'data' from 0 to n - 1 using average rank for ties.
    """
    dd = {}
    for i, x in enumerate(sorted(zero_if_none(data))):
        if x is None:
            x = 0
        try:
            s, c = dd[x]
            dd[x] = (s + i + 1, c + 1)
        except KeyError:
            dd[x] = (i + 1, 1)
    return [dd[x][0] / dd[x][1] for x in data]


def t_limits(n, p):
    """
    Trim/winsorize Limit offsets for 'n' values and proportion 'p', constrained
    to (0 <= p <= .33) and 'n' >= 3.
    """
    if n < 3:
        raise ValueError("Not enough data: %d" % n)
    p = min(max(p, 0), .33)
    li = max(floor(n * p), 1)
    ui = min(ceil(n * (1 - p)), n - 1)
    return li, ui


def trim(data, tp):
    """
    Trim proportion 'tp' from each end of 'data' considered in sorted order.
    """
    li, ui = t_limits(len(data), tp)
    return sorted(data)[li:ui]


def trim_mean(data, tp=.2):
    """
    Trimmed mean that removes proportion 'tp' from both ends of 'data',
    considered in sorted order. Proportion 'tp' constrained to (0 <= tp <= .33).
    At least three values needed.
    """
    tp = min(max(tp, 0), .33)
    return np.mean(trim(data, tp))


def winsorize(data, wp=.25):
    """
    Winsoried values in 'data' cby flattening the proportion 'wp' from both
    ends considered in sorted order. Example: if data =
    [1,2,3,4,5,6,7,8] then the winsorized values are [3,3,3,4,5,6,6,6].
    """
    n = len(data)
    li, ui = t_limits(n, wp)
    xs = sorted(data)
    return [xs[li] if i < li else xs[ui] if i >= ui else xs[i]
            for i in range(n)]


def w_std(data, wp=.2):
    """
    Winsoried standard deviation for values in 'data' using proportion 'wp'.
    """
    wp = min(max(wp, 0), .33)
    wx = winsorize(data, wp)
    return np.std(wx, ddof=1)


def w_stderr(data, wp=.2):
    """
    Winsoried standard error for values in 'data' using proportion 'wp'.
    """
    wp = min(max(wp, 0), .33)
    wx = winsorize(data, wp)
    sd = np.std(wx, ddof=1)
    return sd / (sqrt(len(data) * (1 - (wp * 2))))


def wx_test(test, base=None):
    """
    Wilcoxen signed ranks test for paired values or comparing against a
    standard, where 'test' has at least 12 values to test and 'base' can be
    matching values, a single value to subtract from each 'test' value or None,
    which assumes 'test' to already be differences. Returns normalized score.
    """
    n = len(test)
    if n < 3:
        raise ValueError("Not enough data.")
    data = test
    if base is not None:
        if hasattr(base, '__len__'):
            if len(base) != len(base):
                raise ValueError("Base value must match test values.")
            data = [x - y for x, y in zip(test, base)]
        else:
            data = [x - base for x in test]
    rs = 0
    for i, x in enumerate(sorted(data, key=abs)):
        if x > 0:
            rs += i + 1
        elif x < 0:
            rs -= i + 1
    return rs / sqrt(((n * (n + 1)) * ((2 * n) + 1)) / 12)
