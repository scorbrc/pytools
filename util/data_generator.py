"""
Data generator functions.
"""
import datetime as dt
from math import cos, pi, sin
from random import choice, normalvariate, random, randint, weibullvariate
import numpy as np


def add_cycle(values, pn, a, b, hm=2, sti=0):
    """
    Add a cycle to 'values' with 'pn' periods, coefficients 'a' for sine
    and 'b' for cosine, harmonic 'hm' and starting at period 'sti'.
    """
    return [x + (x * a * sin((hm * pi * (sti + t + 1)) / pn)) +
            (x * b * cos((hm * pi * (sti + t + 1)) / pn))
            for t, x in enumerate(values)]


def adjust_mean(values, target, precision=.001):
    """
    Incrementally adjusts the mean of 'values' to match 'target' within
    the given 'precision'.
    """
    adj_values = [x for x in values]
    for k in range(10):
        df = np.mean(adj_values) - target
        if abs(df) / target < precision:
            break
        for i in range(len(adj_values)):
            if adj_values[i] > df:
                adj_values[i] -= df
            adj_values[i] = max(adj_values[i], 0)
    return adj_values


def any_date_last_week():
    """ Randomly picks a date in the past week. """
    return dt.datetime.now() - dt.timedelta(seconds=randint(1, 60 * 60 * 24 * 7))


def change(data, cr, si, ei):
    """ Change values in 'data' by 'cr' starting at 'si' and ending at 'ei'. """
    return [x * cr if i >= si and i <= ei else x
            for i, x in enumerate(data)]


def gen_cycle(mu, day_n, data_n, last_date=None,
              cycle='mid', sc=2, trend_f=None):
    """
    Generate a random cycle of dates and values with mean 'mu', 'day_n'
    periods per day, 'data_n' periods, optional 'last_date'
    (default current date/time), 'cycle' intensity (low, mid, high)
    and scaling factor 'sc', lower the value the spiker the values.
    """
    # Generate dates and random flat values.
    dates = gen_dates(day_n, data_n, last_date)
    values = (np.random.weibull(sc, data_n) +
              np.random.normal(1, .25, data_n)) * mu / 2

    # Allocate cycles.
    if cycle == 'low':
        a1, b1 = rand_pair(.01, .05)
        a2, b2 = rand_pair(.02, .04)
        a3, b3 = rand_pair(.005, .01)
        a = .01 + (random() * .03)
    elif cycle == 'mid':
        a1, b1 = rand_pair(.1, .4)
        a2, b2 = rand_pair(.05, .2)
        a3, b3 = rand_pair(.03, .05)
        a = .1 + (random() * .2)
    elif cycle == 'high':
        a1, b1 = rand_pair(.2, .6)
        a2, b2 = rand_pair(.1, .5)
        a3, b3 = rand_pair(.1, .3)
        a = .2 + (random() * .3)
    else:
        raise ValueError("Invalid %s" % cycle)

    # Add the cycles to the values.
    s1 = add_cycle(values, day_n, a1, b1, hm=2)
    s2 = add_cycle(s1, day_n, a2, b2, hm=4)
    s3 = add_cycle(s2, day_n / 24, a3, b3, hm=16)
    values = list(s3)

    # Adjust for weekdays/weekends.
    we_adj = 1 - a
    wd_adj = 1 + (a * 2 / 5)
    for i in range(len(dates)):
        values[i] *= wd_adj if dates[i].weekday() < 5 else we_adj
    if trend_f is not None:
        values = trend(values, trend_f)

    # Adjust for the desired mean.
    values = [max(x, 0) for x in adjust_mean(values, mu)]

    return dates, values


def gen_dates(day_n, data_n, last_date=None):
    dates = []
    secs = (60 * 60 * 24) / day_n
    if last_date is not None:
        es = int(last_date.timestamp())
    else:
        es = int(dt.datetime.now().timestamp())
    now = dt.datetime.fromtimestamp(int(es / secs) * secs)
    for i in range(data_n):
        dates.append(now - dt.timedelta(seconds=secs * (data_n - i)))
    return dates


def gen_flat(mu, day_n, data_n, last_date=None, sc=2, trend_f=None):
    dates = gen_dates(day_n, data_n)
    values = [normalvariate(mu/2, mu/6) + weibullvariate(mu/2, sc)
              for _ in range(data_n)]
    if trend_f is not None:
        values = trend(values, trend_f)
    values = [max(x, 0) for x in adjust_mean(values, mu)]
    return dates, values


def rand_pair(lv, uv):
    """
    A random pair of values between 'lv' and 'uv', inclusive. Either
    the first or second random value will positve or negative.
    """
    s = choice((1, -1))
    r1 = lv + random() * (uv - lv) * s
    r2 = lv + random() * (uv - lv) * -s
    return r1, r2


def trend(data, a=.01):
    """ Ramp increase/decrease for a: -1 < a < 1 of 'values'. """
    return [max(x * (1 + (random() * a * t)), 0)
            for t, x in enumerate(data)]
