""" Functions for finding a smoothed line among a time-series or values. """
from math import ceil, sqrt
from util.stat_utils import trim_mean


def def_coef(cf, dx):
    if cf is None:
        return dx
    return min(max(cf, 1e-6), 1 - 1e-6)


def front_load(i, f):
    """
    front load smoothing coefficient or scaling factor 'f' based on period
    index 'i' to quickly stabilize models.
    """
    return max(2 / (i + 2), f)


def smooth(i, f, x, y):
    """
    Exponentially smooth 'x', where 'i' is the period index, 'f' is the
    smoothing coefficient and 'y' is the last smoothed value.
    """
    a = front_load(i, f)
    return (a * x) + ((1 - a) * y)


def des(data, a=None, b=None, d=None):
    """
    Double exponential smoothing of level and trend for values in 'data',
    where 'a' the smoothing coefficent for the level, 'b' is the smoothing
    coefficient for the trend and 'd' is a damping coefficient.
    """
    n = len(data)
    a = def_coef(a, 2 / sqrt(n))
    b = def_coef(b, 2 / (n / 2 - 1))
    d = def_coef(d, 1 - (1 / sqrt(n)))
    u1 = b1 = 1
    for i, x in enumerate(data):
        yield max(u1 + b1, 0) if i >= 5 else x
        u0 = u1
        b0 = b1 * d
        u1 = smooth(i, a, x, u0 + b0)
        b1 = smooth(i, b, u1 - u0, b1)


def ghf(data, g=.1, h=.01):
    """
    A baysian g-h filter for values in 'data', where 'g' is the scaling factor
    for the measurements and 'h' is the scaling factor for change in
    measurements. Both are expected to be 0 < g, h, < 1.
    """
    n = len(data)
    g = def_coef(g, 2 / sqrt(n))
    h = def_coef(h, 2 / (n / 2 - 1))
    x1 = dx = 1
    for i, x0 in enumerate(data):
        yield x1 if i >= 5 else x0
        er = x0 - (x1 + dx)
        dx = dx + front_load(i, h) * er
        x1 = x1 + dx + front_load(i, g) * er


def kfs(data, a=.05):
    """
    Kalman filter smoother for values in 'data', where 'a' is a smoothing
    coefficient for updating the model.
    """
    n = len(data)
    a = def_coef(a, 1 / sqrt(n))
    ev = pv = y = 1
    for i, x in enumerate(data):
        y = ((x * pv) + (y * ev)) / (pv + ev)
        b = front_load(i, a)
        ev = (b * abs(x - y)) + ((1 - b) * ev)
        pv = (1 / ((1 / pv) + (1 / ev))) + (ev * b)
        yield y if i >= 5 else x


def ses(data, a=.1):
    """
    Single exponential smoother for values in 'data' for only level, where
    'a' is the smoothing coefficient (0 <= a <= 1). Higher the value the
    faster the model updates.
    """
    n = len(data)
    a = def_coef(a, 3 / sqrt(n))
    y = 1
    for i, x in enumerate(data):
        yield y if i >= 5 else x
        y = smooth(i, a, x, y)


def sma(data, window_n=None, agg_fn=trim_mean):
    """
    Sliding window moving average smoother. 'window_n' is the number of
    periods in the window, defaulting to square root of number of values
    in data, and 'agg_fn' is the function to aggregate the values in the
    window (mean, median, trim_mean).
    """
    data_n = len(data)
    if window_n is None:
        window_n = max(ceil(sqrt(data_n) / 2), 3)
    slide_n = (window_n * 2) // 3
    sm_data = []
    window = []
    start_i = 0
    for i in range(data_n):
        if i - start_i >= window_n or i == data_n - 1:
            if i == data_n - 1 or len(window) == 0:
                window.append(data[i])
            sm_data.append(agg_fn(window))
            old_start_i = start_i
            while start_i < data_n and start_i - old_start_i < slide_n:
                window.remove(data[start_i])
                start_i += 1
        window.append(data[i])
    scale = len(sm_data) / data_n
    return [sm_data[int(i * scale)] for i in range(len(data))]
