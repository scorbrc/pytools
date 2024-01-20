"""
Bootstrap functions for constructing confidence intervals that reflect the
distribution of data. Two types of bootstrap: T-based and percentile. The
T-based uses a given mean and standard error of mean function. By default this
is mean and stderr. The more robust t_mean and w_stderr can be used.
"""
from math import ceil, sqrt
import numpy as np
import scipy.stats as ss
from random import choices


def conf_limits(n, cp):
    """
    Calculate confidence lower and upper percentle limits starting from the
    given confidence proportion 'cp' and adjusting for small 'n'.
    """
    cf = min(max(cp * sqrt(n / (n - 1)), 1e-6), 1 - 1e-6)
    a = (1 - cf) / 2
    return a * 100, (1 - a) * 100


def repls(n, bn=30, br=2000):
    """
    Estimates number of replications needed based on data size, the more data
    the less replications needed. 'n' is the number of values in the data,
    'bn' is the minimum base of values to reach maximum replications and
    'br' is the base number of replications. bn=30 and br=2000 means if 30 or
    less values then use 2000 replications and if 2000 or more values
    then use 30 replications.
    """
    return min(max(ceil(((br * bn) / (n * br)) * br), bn), br)


def p_conf(data, cp=.99, agg_fn=np.mean):
    """
    Percentile based bootstrapped confidence interval using resampling to
    calculate lower and upper limits that will reflect the distribution of
    values in 'data', according to 'agg_fn' aggregate function. The function
    takes one parameter, the values in 'data' and produces a scalar aggregate.
    The function can be mean, median, percentile and so on. Confidence
    percentile (0 < 'cp' < 1) controls width of the interval. A cp=.99
    would produce lower and upper values that represent 99% of the possible
    values from the 'agg_fn' aggregate function. At least five distinct values
    are needed in 'data' for percentile bootstrapping.
    """
    lc = uc = 0
    if len(set(data)) >= 5:
        repl_n = repls(len(data))
        stats = [agg_fn(data)]
        for i in range(repl_n):
            bx = choices(data, k=len(data))
            stats.append(agg_fn(bx))
        lc, uc = np.percentile(stats, conf_limits(len(data), cp))
    return lc, uc


def t_conf(data, cp=.99, loc_fn=np.mean, var_fn=ss.sem):
    """
    T based bootstrapped confidence interval using resampling to calculate lower
    and upper limits that will reflect the distribution of values in 'data'.
    where 'cp' is the confidence proportion (0 < cp < 1), using mean function
    'loc_fn' and standard error of the mean function 'var_fn'. Returns
    confidence interval, lower and upper bound.
    """
    cp = min(max(cp, 1e-6), 1 - 1e-6)
    lc = uc = 0
    if len(set(data)) >= 5:
        repl_n = 1000  # repls(len(data), 30, 1000)
        u0 = loc_fn(data)
        s0 = var_fn(data)
        tss = []
        for i in range(repl_n):
            x1 = choices(data, k=len(data))
            se = var_fn(x1)
            tss.append((loc_fn(x1) - u0) / se if se > 0 else 0)
        a = (1 - cp) / 2
        t0, t1 = np.percentile(tss, (a * 100, (1 - a) * 100))
        lc = u0 - s0 * t1
        uc = u0 - s0 * t0
    return lc, uc
