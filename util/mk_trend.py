from collections import defaultdict
from math import copysign, sqrt


def count_values(data):
    """ Count occurrences of unique values. """
    vc = defaultdict(int)
    for x in data:
        vc[x] += 1
    return vc


def count_tied_groups(vc):
    """ Count tied groups based on unique value counts. """
    tg = 0
    for c in vc.values():
        tg += (c * (c - 1)) * ((2 * c) + 5)
    return tg


def ranksums_trend(data):
    """ Rolling ranksums. """
    rs = 0
    for i, y in enumerate(data[:-1]):
        for x in data[i + 1:]:
            if x < y:
                rs -= 1
            elif x > y:
                rs += 1
    return rs


def stdev_trend(data):
    " Standard deviation, accounting for tied groups. "
    n = len(data)
    tg = count_tied_groups(count_values(data))
    return sqrt(((n * (n - 1) * (2 * n + 5)) - tg) / 18)


def mk_trend(data):
    """
    Mann-Kendall trend test for 'data', assumed to be a time-series.
    Compares before/after ranks for each value, generating a normalized
    test scorevadjusted for any tied groups of values. Algorithm described
    in https://vsp.pnnl.gov/help/Vsample/Design_Trend_Mann_Kendall.htm.
    """
    n = len(data)
    if n < 12:
        raise ValueError("Not enough data.")
    sd = stdev_trend(data)
    if sd > 0:
        rs = ranksums_trend(data)
        return (rs - copysign(1, rs)) / sd
    return 0
