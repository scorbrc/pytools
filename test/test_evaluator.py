from collections import defaultdict
import numpy as np
from util.open_record import OpenRecord
from util.describer import describe


class TestEvaluator:

    def __init__(self, test_name):
        self.test_name = test_name
        self.counts = defaultdict(int)
        self.tss = {}
        self.ttd = []

    def count_test(self, cr, test):
        self.tss.setdefault(cr, [])
        self.tss[cr].append(test.score)
        if cr < 1.0:
            if test.is_under:
                self.counts['tp'] += 1
            else:
                self.counts['fn'] += 1
        elif cr > 1.0:
            if test.is_over:
                self.counts['tp'] += 1
            else:
                self.counts['fn'] += 1
        else:
            if test.is_under or test.is_over:
                self.counts['fp'] += 1
            else:
                self.counts['tn'] += 1
        self.counts['ct'] += 1

    def count(self, cr, cp_k, ci, max_ts, h):
        self.counts['ct'] += 1
        self.tss.setdefault(cr, [])
        self.tss[cr].append(max_ts)
        if max_ts > h:
            if cr > 1:
                self.counts['tp'] += 1
                self.ttd.append(cp_k - ci)
            else:
                self.counts['fp'] += 1
        elif max_ts < -h:
            if cr < 1:
                self.counts['tp'] += 1
                self.ttd.append(cp_k - ci)
            else:
                self.counts['fp'] += 1
        else:
            if cr != 1:
                self.counts['fn'] += 1
            else:
                self.counts['tn'] += 1

    def report(self):
        if len(self.tss) < 3:
            raise ValueError("Need at least 3 descs.")
        dss_ts = [describe(self.tss[cr],
                           self.test_name + '_%.3f' % cr,
                           full_pcts=True)
                  for cr in sorted(self.tss)]

        low, mid, high = sorted(self.tss)
        minv = min(self.tss[mid])
        lc = sum([1 for x in self.tss[low] if x < minv])
        maxv = max(self.tss[mid])
        uc = sum([1 for x in self.tss[high] if x > maxv])
        eff = (lc + uc) / (len(self.tss[low]) + len(self.tss[high]))

        ttd = np.mean(self.ttd) if len(self.ttd) else 0
        return OpenRecord(
            test_name=self.test_name,
            lp01=dss_ts[0].p005,
            lp99=dss_ts[0].p995,
            mp01=dss_ts[1].p005,
            mp99=dss_ts[1].p995,
            up01=dss_ts[2].p005,
            up99=dss_ts[2].p995,
            tp=self.counts['tp'] / self.counts['ct'],
            fp=self.counts['fp'] / self.counts['ct'],
            tn=self.counts['tn'] / self.counts['ct'],
            fn=self.counts['fn'] / self.counts['ct'],
            eff=eff,
            ttd=ttd
        )
