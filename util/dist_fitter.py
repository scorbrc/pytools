"""
Fits a distribution for a given dataset for generating test data.
"""
from inspect import getmembers, isfunction
from io import StringIO
import numpy as np
import scipy.stats as ss
from time import time
from util.stat_utils import fit
import warnings
from util.describer import describe
from util.open_record import OpenRecord


class DistributionGenerator:

    EXCLUDES = set((
        'betaprime',
        'crystalball',
        'f',
        'foldcauchy',
        'foldnorm',
        'halfcauchy',
        'kstwo',
        'ksone',
        'kstwobign',
        'ncf',
        'nct',
        'ncx2',
        'pearson3',
        'rdist',
        'rv_continuous',
        'rv_histogram',
        'skewcauchy',
        'studentized_range',
        't',
        'wrapcauchy'
    ))

    def __init__(self, **rec):
        self.__name = rec['name']
        self.__desc = rec['desc']
        if isinstance(rec['dist'], str):
            self.__dist = getattr(ss, rec['dist'])
        else:
            self.__dist = rec['dist']
        self.__args = rec['args']
        self.__loc = rec['loc']
        self.__scale = rec['scale']
        self.__mape = rec['mape']
        self.__mpe = rec['mpe']
        self.__data_ds = OpenRecord(rec['data_ds'])
        self.__test_ds = OpenRecord(rec['test_ds'])
        self.__sse = rec['sse']
        self.__secs = rec['secs']

    @staticmethod
    def create(name, data):
        n = len(data)
        if n < 30:
            raise ValueError("Not enough data.")
        st = time()
        model = OpenRecord(name=None, desc=None, dist=None, sse=np.inf)
        data = np.asarray(data)
        hist, edges = np.histogram(data, bins=200)
        edges = (edges + np.roll(edges, -1))[: -1] / 2
        for dist_name, dist in DistributionGenerator.get_dists():
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore')
                    params = dist.fit(data)
                    pdf = dist.pdf(edges,
                                   loc=params[-2],
                                   scale=params[-1],
                                   *params[:-2])
                    sse = np.sum(np.power(hist - pdf, 2))
                    if model.sse > sse > 0:
                        model.name = name
                        args = ['%.4f' % p for p in params[:-2]]
                        model.desc = "%s(%s,loc=%.4f,scale=%.4f)" % \
                            (name, ','.join(args), params[-2], params[-1])
                        model.dist = dist
                        model.loc = params[-2]
                        model.scale = params[-1]
                        model.args = params[:-2]
                        model.sse = sse
            except (FloatingPointError, ValueError, OverflowError):
                pass

        if model.dist is not None:
            try:
                test = [max(x, 0) for x in model.dist.rvs(
                    *model.args, loc=model.loc, scale=model.scale, size=max(len(data), 200))]
                model.data_ds = describe(data, 'data', full_pcts=True)
                model.test_ds = describe(test, 'test', full_pcts=True)
                model.mape, model.mpe = fit(data, test)
                model.secs = time() - st
                return DistributionGenerator(**model)
            except (AttributeError, FloatingPointError) as ex:
                print(model, ex)
        return None

    @staticmethod
    def from_json(src):
        rec = json.loads(src)
        return DistributionGenerator(**rec)

    def generate(self, n=1):
        return self.dist.rvs(*self.args, loc=self.loc,
                             scale=self.scale, size=n)

    @staticmethod
    def get_dists():
        """ Get continous distributions from scipy.stats. """
        for x in getmembers(ss):
            if not isfunction(x[1]):
                if hasattr(x[1], 'ppf'):
                    if 'continuous' in str(x[1]):
                        if x[0] not in DistributionGenerator.EXCLUDES:
                            yield x

    @staticmethod
    def to_json(self):
        return json.dumps({
            "name": self.__name,
            "desc": self.__desc,
            "dist": self.__dist,
            "args": self.__args,
            "loc": self.__loc,
            "scale": self.__scale,
            "mape": self.__mape,
            "mpe": self.__mpe,
            "data_ds": self.__data_ds,
            "test_ds": self.__test_ds,
            "sse": self.__sse,
            "secs": self.__secs
        })

    def __str__(self):
        so = StringIO()
        print("DistributionGenerator for %s" % self.__name, file=so)
        dist_name = str(self.__dist).partition(' ')[0].rpartition('.')[2]
        print("    %s(%s,loc=%.4f,scale=%.4f)" %
              (dist_name, self.__args, self.__loc, self.__scale),
              file=so)
        print("    mape:  %.3f" % self.__mape, file=so)
        print("    mpe:   %.3f" % self.__mpe, file=so)
        desc = OpenRecord.to_text_rows(
            (self.__data_ds, self.__test_ds), indent=4)
        print("    Desc stats:\n    %s" % desc, file=so)
        print("    secs   : %.3f" % self.__secs, file=so)
        return so.getvalue()
