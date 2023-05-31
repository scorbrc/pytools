"""
Testers for determining when a change has occurred in a series of values.
"""
from bisect import bisect_left
from util.stat_utils import mean, std


def pcusum(data, base_n, k):
    base = sorted(data[:base_n])
    n = base_n + .5
    sl = sh = 0
    for x in data[base_n:]:
        ts = ((bisect_left(base, x) / n) - .5) * 2
        sl = min(sl + ts + k, 0)
        sh = max(sh + ts - k, 0)
        yield max(sl, sh, key=abs)


def pewma(data, base_n, a):
    base = sorted(data[:base_n])
    n = base_n + .5
    sl = sh = 0
    for x in data[base_n:]:
        ts = ((bisect_left(base, x) / n) - .5) * 2
        sl = min((a * ts) + ((1 - a) * sl), 0)
        sh = max((a * ts) + ((1 - a) * sh), 0)
        yield -abs(sl)**a if abs(sl) > sh else sh**a


def tcusum(data, base_n, k):
    sl = sh = 0
    data = [x**(1/2) if x > 1 else x for x in data]
    mu = mean(data[:base_n])
    sd = std(data[:base_n])
    for x in data[base_n:]:
        ts = (x - mu) / (sd * 2) if sd > 0 else 0
        sl = min(sl + ts + k, 0)
        sh = max(sh + ts - k, 0)
        yield max(sl, sh, key=abs)


def tewma(data, base_n, a):
    sl = sh = 0
    g = (a / (2 - a))**(1/2)
    data = [x**(1/2) if x > 1 else x for x in data]
    mu = mean(data[:base_n])
    sd = std(data[:base_n])
    for x in data[base_n:]:
        ts = (x - mu) / (sd * 2) if sd > 0 else 0
        sl = min((a * ts) + ((1 - a) * sl), 0)
        sh = max((a * ts) + ((1 - a) * sh), 0)
        yield max(sl, sh, key=abs) / g
