from math import sqrt
from .util_tools import zero_if_none


def median(data):
    n = len(data)
    m = n // 2
    mx = sorted(data)
    return mx[m] if n % 2 == 1 else (mx[m] + mx[m-1]) / 2


def mean(data):
    """ Arithmetic mean for values in  'data'. """
    return sum(data) / len(data) if len(data) > 0 else 0


def percentile(data, pcs):
    """
    Percentiles 'pcs' (0 <= pc <= 100) calculated for values in 'data',
    At least three values needed.
    """
    if not isinstance(pcs, (list, tuple)):
        pcs = [pcs]
    pvs = [0] * len(pcs)
    if len(data) >= 3:
        xs = sorted(data)
        for k, pc in enumerate(pcs):
            r = (len(xs) - 1) * pc / 100
            i = int(r)
            if i < len(xs) - 1:
                pvs[k] = xs[i] + (xs[i + 1] - xs[i]) * (r - i)
            else:
                pvs[k] = xs[-1]
    return pvs[0] if len(pvs) == 1 else pvs


def rankdata(data):
    """
    Ranks values in 'data' from 0 to n - 1 using average rank for ties.
    """
    dd = {}
    data = zero_if_none(data)
    for i, x in enumerate(sorted(data)):
        if x is None:
            x = 0
        try:
            s, c = dd[x]
            dd[x] = (s + i + 1, c + 1)
        except KeyError:
            dd[x] = (i + 1, 1)
    return [dd[x][0] / dd[x][1] for x in data]


def std(data, mu=None):
    """ Sample standard deviation of the values in 'data'. """
    if len(data) >= 2:
        if mu is None:
            mu = mean(data)
        return sqrt(sum([(x - mu)**2 for x in data]) / (len(data) - 1))
    return 0


def stderr(data, mu=None):
    """ Standard error of the mean for values in 'data'. """
    return std(data, mu) / sqrt(len(data))
