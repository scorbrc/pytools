from math import ceil, floor, sqrt
from util.stat_utils import (
    mean,
    median,
    pct_diff,
    std,
    stderr
)
from util.transform import fr_sqrt_trans, to_sqrt_trans


def est(data):
    """
    Default estimator for values in 'data', returning mean and standard error.
    """
    mu = mean(data)
    se = stderr(data, mu)
    return mu, se


def m_est(data, cf=2, pct_imp=.01, max_iters=12):
    """
    Robust M estimate for values in 'data'. Outliers are weighted towards
    the mean using an iterative fitting process. 'cf' is the convergence
    factor that determines how aggressive the weighting is. 'pct_imp' is
    the percentage improvement needed to continue iteration. Estimation
    stops once the percentage improvement from the last iteration falls
    below 'pct_imp'. 'max_iters' is the maximum iterations to attempt.
    Returns M estimate and standard error.
    """
    n = len(data)
    if n < 5:
        raise ValueError("Not enough data.")
    m1 = median(data)
    md = median([abs(x - m1) for x in data])
    tv = md * cf
    wt = [1] * n
    for k in range(12):
        m0 = m1
        ws = 0
        for i, x in enumerate(data):
            if x < m1 - tv:
                wt[i] = -tv / (x - m1)
            elif x > m1 + tv:
                wt[i] = tv / (x - m1)
            ws += (wt[i] * x)
        m1 = ws / n
        if abs(pct_diff(m1, m0)) < .01:
            break
    se = std([x*w for x, w in zip(data, wt)], m1) / sqrt(wt.count(1))
    return m1, se


def trim_est(data, p=.2):
    """
    Trimmed mean estimator for values in 'data'. Proportion 'p'
    (0 <= 'p' <= .4) is trimmed from both ends of 'data' considered in
    sorted order. The standard error uses winsorized values that are
    flattened at both end. For example, if 'p'=.2 and 'data' is
    [1,2,3,4,5,6,7,8] then the trimmed values used for the mean would
    be [2,3,4,5,6,7] and winsorized values used for the standard error
    would be [2,2,3,4,5,6,7,7]. Returns trimmed mean and winsorized
    standard error.
    """
    n = len(data)
    if n < 3:
        raise ValueError("Not enough data.")
    p = min(max(p, 0), .4)

    li = max(floor(n * p), 1)
    ui = min(ceil(n * (1 - p)), n - 1)
    xs = sorted(data)
    mu = mean(xs[li:ui])

    for i, x in enumerate(xs):
        if i < li:
            xs[i] = xs[li]
        elif i >= ui:
            xs[i] = xs[ui]
    se = std(xs) / sqrt(n * (1 - (p * 2)))

    return mu, se
