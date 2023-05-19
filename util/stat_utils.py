"""
Statistical utility functions.
"""
from bisect import bisect_left
from collections import defaultdict
import datetime as dt
from math import ceil, copysign, floor, sqrt
from .base_stats import (
    mean,
    percentile,
    rankdata,
    std,
    stderr
)
from .open_record import OpenRecord

MIN_SCORE = -6 + 1e-6
MAX_SCORE = 6 + 1e-6
PERCENTILES = (0, .1, .5, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.5, 99.9, 100)


def c4(n):
    """ Correction for small sample sizes as used in control charting. """
    return (4 * max(n, 2) - 4) / (4 * max(n, 2) - 3)


def describe(data, name='desc', full_pcts=False):
    """
    Descriptive statistics for 'data' with label 'name'. Use 'full_pcts' to
    produce both lower and upper percentiles.
    n - number of values
    mu - arithmetic mean
    sd - standard deviation
    cv - coefficient of variation: sd/mu
    kr - kurtosis
    p00, p005 ... p50 ... p995, p100 are the percentiles.
    """
    n = len(data)
    ds = OpenRecord(name=name, n=n, mu=0, sd=0)
    pcts = PERCENTILES
    if not full_pcts:
        pcts = pcts[7:]
    for p in pcts:
        if isinstance(p, int):
            ds['p%02d' % p] = 0
        else:
            ds['p%03d' % (p * 10)] = 0
    if n >= 3:
        try:
            ds.mu = mean(data)
            ds.sd = std(data)
            for p, v in zip(pcts, percentile(data, pcts)):
                if isinstance(p, int):
                    ds['p%02d' % p] = v
                else:
                    ds['p%03d' % (p * 10)] = v
        except FloatingPointError:
            pass
    return ds


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
        for i, (x, y) in enumerate(zip(obs, eps)):
            pcd = pct_diff(x, y)
            mape += abs(pcd)
            mpe += pcd
    except FloatingPointError:
        pass
    return mape / len(obs), mpe / len(obs)


def median(data):
    """ The 50th peercentile value in 'data'. """
    return percentile(data, 50)


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
    return percentile(data, 50)


def p90(data):
    """ The 90th peercentile value in 'data'. """
    return percentile(data, 90)


def p95(data):
    """ The 95th peercentile value in 'data'. """
    return percentile(data, 95)


def p99(data):
    """ The 99th peercentile value in 'data'. """
    return percentile(data, 99)


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


def pscores(data):
    """
    Convert 'data' to percentile scores (-1 <= pscore <= 1). Use average rank
    for duplicate values.
    """
    n = len(data) + .5
    return [((r / n) - .5) * 2 for r in rankdata(data)]


def rs_test(base, test):
    """
    Rank sums test comparing 'base' values to 'test' values. Each must have
    at least 4 values and 12 overall values. Average rank used for ties.
    Returns a normalized test score.
    """
    n = len(base)
    m = len(test)
    if n >= 4 and m >= 4 and n + m >= 12:
        bx = sorted(base)
        rs = 0
        for x in test:
            i = bisect_left(bx, x)
            c = bx.count(x)
            rs += i + (c / 2) - (n / 2)
        return rs / sqrt((n * m * (n + m + 1)) / 12)
    return 0


def tcf(n, z):
    """
    Adjusts score 'z' down by the approximate T critical value with 'n'
    degrees of freedom. The greater 'n' is the less the correction will be.
    """
    return (z * 2) - (z + ((z**3 + z) / (4 * n)) +
                      (((5 * z**5) + (16 * z**3) + (3 * z)) / (96 * n**2)))


def ti_test(base, test):
    """
    Independent T test comparing 'base' values to 'test' values. Each must have
    at least 4 values with 12 overall values. Returns a normalized test score.
    """
    m = len(test)
    n = len(base)
    if n < 4 or m < 4 or n + m < 12:
        return 0
    se = (stderr(base) * (n / (n + m))) + (stderr(test) * (m / (n + m)))
    zs = ((mean(test) - mean(base)) / (se * 2))
    return tcf(n + m - 2, zs)


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
    return mean(trim(data, tp))


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


def w_stderr(data, wp=.2):
    """
    Winsoried standard error for values in 'data' using proportion 'wp'.
    """
    wp = min(max(wp, 0), .33)
    wx = winsorize(data, wp)
    sd = std(wx)
    return sd / (sqrt(len(data) * (1 - (wp * 2))))


def wx_test(test, base=None):
    """
    Wilcoxen signed ranks test for paired values or comparing against a
    standard, where 'test' has at least 12 values to test and 'base' can be
    matching values, a single value to subtract from each 'test' value or None,
    which assumes 'test' to already be differences. Returns normalized score.
    """
    n = len(test)
    if n < 12:
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


def zscores(data):
    """
    Convert 'data', which must have at least three values, to Z scores with
    mean of 0 and standard deviation of 1.
    """
    if len(data) < 3:
        return [0] * len(data)
    u = mean(data)
    s = std(data)
    return [(x - u) / s for x in data]
