""" Transform functions to reduce variability in data. """
from math import exp, log, sqrt


def fr_log_trans(x):
    """ Untransform a log transform using 'to_log_trans'. """
    try:
        return exp(x)-1 if x > 1 else x
    except TypeError:
        return [exp(v)-1 if v > 1 else v for v in x]


def fr_sqrt_trans(x):
    """ Untransform a square root transform using 'to_sqrt_trans'. """
    try:
        return x**2 if x > 1 else x
    except TypeError:
        return [sqrt(v) if v > 1 else v for v in x]


def to_log_trans(x):
    """ Log transform 'x', which can be a scale or sequence. """
    try:
        return log(x+1) if x > 1 else x
    except TypeError:
        return [log(v+1) if v > 1 else v for v in x]


def to_sqrt_trans(x):
    """ Square root transform 'x', which can be a scale or sequence. """
    try:
        return sqrt(x) if x > 1 else x
    except TypeError:
        return [sqrt(v) if v > 1 else v for v in x]
