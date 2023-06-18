from math import sqrt
from util.stat_utils import median, pct_diff, std


def m_estimate(data, cf=2):
    """
    Robust measure of location for 'data'. Outliers are weighted towards
    the mean. 'cf' is the convergence factor that determines how aggressive
    data are weighted.
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
                wt[i] = 1 + (tv / (m1 - x))
            elif x > m1 + tv:
                wt[i] = (tv / (x - m1))
            ws += (wt[i] * data[i])
        m1 = ws / n
        if m0 + m1 > 0 and abs(pct_diff(m1, m0)) < .01:
            break
    se = std([x * w for x, w in zip(data, wt)], m1) / sqrt(wt.count(1))
    return m1, se, wt
