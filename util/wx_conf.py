import numpy as np
import scipy.stats as ss


def wx_conf(data, cf=.99, prec=.001, max_iters=25):

    h = (1 - cf) / 2
    p0, p50, p100 = np.percentile(data, (0, 50, 100))

    lc0 = p0
    lc1 = p50 / 2
    for i in range(max_iters):
        p = ss.wilcoxon([x - lc1 for x in data])[1]
        d = abs((lc0 - lc1) / 2)
        lc0 = lc1
        lc1 += -d if p > h else d
        if abs((lc1 - lc0) / ((lc1 + lc0) / 2)) <= prec:
            break

    uc0 = p100
    uc1 = p50 + ((uc0 - p50) / 2)
    for i in range(max_iters):
        p = ss.wilcoxon([x - uc1 for x in data])[1]
        d = abs((uc0 - uc1) / 2)
        uc0 = uc1
        uc1 += d if p > h else -d
        if abs((uc1 - uc0) / ((uc1 + uc0) / 2)) <= prec:
            break





    return lc1, uc1
