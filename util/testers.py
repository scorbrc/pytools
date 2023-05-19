from bisect import bisect_left
from math import sqrt
from util.stat_utils import pscores, zscores


def smooth(i, f, x, y):
    a = max(2 / (2 + i), f)
    return (a * x) + ((1 - a) * y)


def cusum(data):
    n = len(data)
    a = 2 / (n - 1)
    wu = wd = 1
    sl = sh = 0
    for i, x in enumerate(data):
        ts = 0
        if i >= 5 and wd > 0:
            ts = (x - wu) / (wd * 2)
            sl = min(sl + ts + 1, 0)
            sh = max(sh + ts - 1, 0)
        wd = smooth(i, a, abs(x - wu), wd)
        wu = smooth(i, a, x, wu)
        yield max(sl, sh, key=abs)
    

def ewma(data):
    n = len(data)
    a = 2 / sqrt(n)
    b = 2 / (n - 1)
    wa = wb = wd = 1
    for i, x in enumerate(data):
        wa = smooth(i, a, x, wa)
        ts = 0
        if i >= 5 and wd > 0:
            ts = (wa - wb) / (wd * 2)
        yield wa, wb, ts
        wd = smooth(i, b, abs(wa - wb), wd)
        wb = smooth(i, b, x, wb)


def tscore(data, a0=.005):
    """
    T-based score in range -6 to 6 generated for each value in 'data'.
    """
    wu = 0
    wd = 1
    for i, x in enumerate(data):
        ts = 0
        if i >= 5 and wd > 0:
            ts = (x - wu) / (wd * 2)
        a1 = max(2 / (i + 2), a0)
        wd = (a1 * abs(x - wu)) + ((1 - a1) * wd)
        wu = (a1 * x) + ((1 - a1) * wu)
        yield min(max(ts, -6), 6)


def pscore(data):
    """
    Percentile score in range -1 to 1 generated for each value in 'data'.
    Uses average rank for duplicates. Proportionally extrapolated between
    values.
    """
    bx = None
    ref_n = int(sqrt(len(data)))
    for k, x in enumerate(data):
        ps = 0
        if k > ref_n and k % ref_n == 0:
            bx = sorted(data[:k - ref_n])
        if bx is not None:
            i = bisect_left(bx, x)
            c = max((bx.count(x) - 1) / 2, 0)
            p = (i + c) / len(bx)
            if i > 0 and i < len(bx) and x != bx[i] and bx[i] != bx[i - 1]:
                p -= ((1 / len(bx)) * (x - bx[i - 1]) / (bx[i] - bx[i - 1]))
            ps = (p - .5) * 2
        yield ps


def pcusum(data, noise=.5):
    """
    Percentile ranked cumulative sums tester for values in 'data'.
    'noise' is the noise factor to subtract from each percentile rank
    before summing. Generates test score for each value where negative
    means current values less than previous values and positive means
    current values greater than past values.
    """
    sl = sh = 0
    for ps in pscores(data):
        sl = min(sl + ps + noise, 0)
        sh = max(sh + ps - noise, 0)
        ts = max(sl, sh, key=abs)
        yield ts


def pewma(data, a=.15):
    """
    Percentile ranked exponential weighted average test for finding
    changepoints in 'data'. Smoothing factor (0 < 'a' < 1) drives how
    fast the model changes. Generates scores in the range of -1 to 1
    that indicates how likely the current values differ from past values.
    """
    sl = sh = 0
    for ps in pscores(data):
        sl = min((a * ps) + ((1 - a) * sl), 0)
        sh = max((a * ps) + ((1 - a) * sh), 0)
        ts = -abs(sl)**a if abs(sl) > abs(sh) else sh**a
        yield ts


def tcusum(data, noise=1):
    """
    T-based cumulative sums tester for values in 'data'. 'noise' is the noise
    factor to subtract from each T-based score before summing. Generates test
    score for each value where negative means current values less than
    previous values and positive means current values greater than past values.
    """
    sl = sh = 0
    for ts in zscores(data):
        sl = min(sl + ts + noise, 0)
        sh = max(sh + ts - noise, 0)
        yield max(sl, sh, key=abs)


def tewma(data, a=.15):
    """
    T-based exponential weighted average test for finding changepoints in
    'data'. Smoothing factor (0 < 'a' < 1) drives how fast the model changes.
    Generates normalized scores that indicates how likely the current values
    differ from past values.
    """
    g = sqrt(a / (2 - a)) * 2
    sl = sh = 0
    for ts in zscores(data):
        sl = min((a * ts) + ((1 - a) * sl), 0)
        sh = max((a * ts) + ((1 - a) * sh), 0)
        ts = max(sl, sh, key=abs) / g
        yield ts
