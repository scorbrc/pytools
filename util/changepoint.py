"""
Functions for finding changepoints in a time-series of data.
"""
from math import sqrt
from util.open_record import OpenRecord
from util.stat_utils import (
    mean,
    median,
    pct_diff,
    rankdata,
    std
)
from util.transform import to_sqrt_trans


def _find_cps_(cpd_fn, loc_fn, data, cpd_h, min_pcd, off_i, min_search_n, cps):

    # Search for a changepoint.
    n = len(data)
    max_ts, cp_k = cpd_fn(data)
    if cp_k > 0:
        # Found a changepoint, determine if significant.
        before = loc_fn(data[:cp_k])
        after = loc_fn(data[cp_k:])
        pcd = pct_diff(after, before)
        if abs(max_ts) >= cpd_h and abs(pcd) >= abs(min_pcd):
            # Record the changepoint with relative offsets.
            cps.append(OpenRecord(
                si=off_i,
                ci=cp_k+off_i,
                ei=off_i+n,
                before=before,
                after=after,
                pcd=pcd,
                ts=max_ts
            ))

            if cp_k >= min_search_n:
                # Search before the current changepoint.
                _find_cps_(cpd_fn,
                           loc_fn,
                           data[:cp_k],
                           cpd_h,
                           min_pcd,
                           off_i,
                           min_search_n,
                           cps)
            if n - cp_k - min_search_n // 2 >= min_search_n:
                # Seach after the current changepoint.
                k = cp_k + min_search_n // 2
                _find_cps_(cpd_fn,
                           loc_fn,
                           data[k:],
                           cpd_h,
                           min_pcd,
                           off_i + k,
                           min_search_n,
                           cps)
    return cps


def rs_cpd(data):
    """
    Find the most likely changepoint in 'data_n' using rank sums testing on a
    sliding window of before/after periods. Index that produces the highest
    absolute test score is the most likely changepoint. Start searching after
    14th period and stop 5 periods from the end to ensure enough data
    to test. Returns normalized test score and offset within 'data'.
    """
    n = len(data)
    cp_k = max_ts = 0
    ranks = [r - (n / 2) for r in rankdata(data)]
    for k in range(14, n - 4):
        sd = sqrt((k * (n - k) * (k + (n - k) + 1)) / 3)
        ts = sum(ranks[k:]) / sd
        if abs(ts) > abs(max_ts):
            cp_k = k
            max_ts = ts
    return max_ts, cp_k


def ti_cpd(data):
    """
    Find the most likely changepoint in 'data_n' using T independent groups
    testing on a sliding window of before/after periods. Index that produces
    the highest absolute test score is the most likely changepoint. Start s
    earching after 14th period and stop 5 periods from the end to ensure
    enough data to test. Returns normalized test score and offset within 'data'.
    """
    n = len(data)
    cp_k = max_ts = 0
    sd = std(data)
    for k in range(14, n - 4):
        u0 = mean(data[:k])
        u1 = mean(data[k:])
        ts = ((u1 - u0) / (sd * 2)) * sqrt((k * (n - k)) / n)
        if abs(ts) > abs(max_ts):
            cp_k = k
            max_ts = ts
    return max_ts, cp_k


def rs_cpd_multi(data, cpd_h=3, min_pcd=10, min_search_n=30):
    """
    Finds potentially multiple changepoints in 'data' using rank sums testing
    on a sliding window of before/after values. Searching proceeds recursively
    before/after the the last changepoint found.
    'cpd_h' is the test score threshold for detecting a changepoint.
    'min_pcd' is the minimum percentage difference between before and after
    values to accept that a test score has detected a changepoint. This
    second test helps control false positives.
    'min_search_n' is the smallest window to search for a changepoint. The
    rank sums test needs at least 20 values to be meaningfull.
    Returns zero or more changepoints. Each Changepoint has starting index,
    change index, ending index, median of the before values,
    median of the after values, percentage difference between before
    and after and test score correspondiong to 'cpd_h'.
    """
    cps = _find_cps_(rs_cpd, median, data, cpd_h, min_pcd, 0, min_search_n, [])
    return sorted(cps, key=lambda cp: cp.ci)


def ti_cpd_multi(data, cpd_h=3, min_pcd=10, min_search_n=30):
    """
    Finds potentially multiple changepoints in 'data' using independent groups
    T testing on a sliding window of before/after values. Searching proceeds
    recursively before/after the the last changepoint found.
    'cpd_h' is the test score threshold for detecting a changepoint.
    'min_pcd' is the minimum percentage difference between before and after
    values to accept that a test score has detected a changepoint. This
    second test helps control false positives.
    'min_search_n' is the smallest window to search for a changepoint. The
    rank sums test needs at least 20 values to be meaningfull.
    Returns zero or more changepoints. Each Changepoint has starting index,
    change index, ending index, median of the before values,
    median of the after values, percentage difference between before
    and after and test score correspondiong to 'cpd_h'.
    """
    data = to_sqrt_trans(data)
    cps = _find_cps_(ti_cpd, mean, data, cpd_h, min_pcd, 0, min_search_n, [])
    return sorted(cps, key=lambda cp: cp.ci)
