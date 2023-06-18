"""
Testers for determining when a change has occurred in a series of values.
"""
from bisect import bisect_left
from math import sqrt
from util.stat_utils import c4, mean, median, rs_test, std
from util.transform import to_sqrt_trans


def cusum(scores, k):
    """
    Cumulative sums tester for test 'scores' using noise factor 'k' (k > 0) to
    subtract/add from each score before adding to upper/lower sums. Sums are
    reset to zero if crossing to the opposite sign. Generates base median/mean,
    test median/mean, and maximum absolute score for each test.
    """
    if k <= 0:
        raise ValueError("Expected k > 0.")
    sl = sh = 0
    for ts in scores:
        sl = min(sl + ts + k, 0)
        sh = max(sh + ts - k, 0)
        yield max(sl, sh, key=abs)


def ewma(scores, a):
    """
    Exponential weighted moving average tester for test 'scores' using
    smoothing factor 'a' (0 < a < 1) to average upper and lower means.
    Means are reset to zero if crossing to the opposite sign. Generates
    base median/mean, test median/mean maximum absolute score for each test.
    """
    if a <= 0 or a >= 1:
        raise ValueError("Expected 0 < a < 1.")
    sl = sh = 0
    for ts in scores:
        sl = min((a * ts) + ((1 - a) * sl), 0)
        sh = max((a * ts) + ((1 - a) * sh), 0)
        yield max(sl, sh, key=abs)


def gti_scores(data, gp_n):
    """
    Grouped T independent scores for values in 'data' using 'gp_n' as
    the group size. Generates scores in range -6 <= ts <= 6.
    """
    gp = []
    means = []
    for x in to_sqrt_trans(data):
        gp.append(x)
        if len(gp) == gp_n:
            m0 = ts = 0
            m1 = mean(gp)
            sd = std(gp) / c4(gp_n)
            if len(means) and sd > 0:
                m0 = mean(means)
                ts = min(max((m1 - m0) / (sd * 2), -6), 6)
            means.append(m1)
            gp = []
            yield min(max(ts, -6), 6)


def grs_scores(data, gp_n):
    """
    Grouped rank sums scores for values in 'data' using 'gp_n' as the group size.
    Generates base median, test median and test score (-6 <= ts <= 6) for each
    group.
    """
    gp = []
    base = []
    for x in data:
        gp.append(x)
        if len(gp) == gp_n:
            median(gp)
            ts = 0
            if len(base) >= gp_n * 2:
                median(base)
                ts = rs_test(base, gp)
            base.extend(gp)
            gp = []
            yield min(max(ts, -6), 6)


def pr_scores(data):
    n = len(data)
    ref_n = int(sqrt(n))
    stage = []
    base = []
    for x in data:
        ps = 0
        if len(base):
            ps = (bisect_left(base, x) / (len(base) + .5) - .5) * 2
        stage.append(x)
        if len(stage) == ref_n:
            base.extend(stage)
            base.sort()
            stage = []
        yield ps


def ti_scores(data):
    n = len(data)
    ref_n = int(sqrt(n))
    stage = []
    base = []
    mu = sd = 1
    for x in to_sqrt_trans(data):
        ts = 0
        if len(base):
            ts = min(max((x - mu) / sd, -6), 6)
        stage.append(x)
        if len(stage) == ref_n:
            base.extend(stage)
            mu = mean(base)
            sd = std(base) / .6745
            stage = []
        yield ts


def grs_cusum(data, gp_n, k):
    """
    Grouped summed ranks cumulative sums tester for values in 'data'
    using 'gp_n' as the group size and 'k' as the noise factor.
    """
    return cusum(grs_scores(data, gp_n), k)


def grs_ewma(data, gp_n, a):
    """
    Grouped summed ranks cumulative sums tester for values in 'data'
    using 'gp_n' as the group size and 'a' as the smoothing coefficient.
    """
    g = min(sqrt(a / (2 - a)) * 2, 1)
    return (ts / g for ts in ewma(grs_scores(data, gp_n), a))


def gti_cusum(data, gp_n, k):
    """
    Grouped T independent cumulative sums tester for values in 'data' using
    'gp_n' as the group size and 'k' as the noise factor.
    """
    return cusum(gti_scores(data, gp_n), k)


def gti_ewma(data, gp_n, a):
    """
    Grouped T independent cumulative sums tester for values in 'data' using
    'gp_n' as the group size and 'a' as the smoothing coefficient.
    """
    g = sqrt(a / (2 - a)) * 2
    return (ts / g for ts in ewma(gti_scores(data, gp_n), a))


def pr_cusum(data, k):
    """
    Percentile ranked cumulative sums tester for the values in 'data' using 'k'
    as the noise factor to remove from scores before summing.
    """
    return cusum(pr_scores(data), k)


def pr_ewma(data, a):
    """
    Percentile ranked exponentially weighted moving averahe tester for the
    values in 'data' using 'a' as the smoothing factor.
    """
    return ((ts**a if ts > 0 else -(abs(ts)**a))
            for ts in ewma(pr_scores(data), a))


def ti_cusum(data, k):
    """
    T independent cumulative sums tester for the values in 'data' using 'k'
    as the noise factor to remove from scores before summing.
    """
    return cusum(ti_scores(data), k)


def ti_ewma(data, a):
    """
    T independent exponentially weighted moving averahe tester for the
    values in 'data' using 'a' as the smoothing factor.
    """
    g = (a / (2 - a))**(1 / 2)
    return (ts / g for ts in ewma(ti_scores(data), a))
