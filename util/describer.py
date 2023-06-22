from collections import deque
import numpy as np
import scipy.stats as ss
from util.open_record import OpenRecord

MAX_VALUES = 50000

PERCENTILES = (0, .1, .5, 1, 5, 10, 25, 50, 75, 90, 95, 99, 99.5, 99.9, 100)


def describe(data, name='desc', full_pcts=False):
    """
    Descriptive statistics for 'data' with label 'name'. Use 'full_pcts' to
    produce both lower and upper percentiles.
    n - number of values
    mu - arithmetic mean
    sd - standard deviation
    cv - coefficient of variation: sd/mu
    kr - kurtosis
    p00, p005 ... p50 ... p995, p100 are the percentiles.
    """
    n = len(data)
    ds = OpenRecord(name=name, n=n, mu=0, sd=0)
    pcts = PERCENTILES
    if not full_pcts:
        pcts = pcts[7:]
    for p in pcts:
        if isinstance(p, int):
            ds['p%02d' % p] = 0
        else:
            ds['p%03d' % (p * 10)] = 0
    if n >= 3:
        try:
            ds.mu = np.mean(data)
            ds.sd = np.std(data, ddof=1)
            for p, v in zip(pcts, np.percentile(data, pcts)):
                if isinstance(p, int):
                    ds['p%02d' % p] = v
                else:
                    ds['p%03d' % (p * 10)] = v
        except FloatingPointError:
            pass
    return ds


class Describer:
    """
    Collects values for descriptive statistics using a fixed size window.
    """

    def __init__(self, name, max_values=MAX_VALUES):
        """
        Create Describer called 'name' that will store at most 'max_values'.
        """
        self.__name = name
        self.__max_values = max_values
        self.__values = deque()

    def add(self, x):
        """
        Add values 'x', rolling off oldest value is 'max_values' reached.
        """
        self.__values.append(x)
        if len(self.__values) > self.__max_values:
            self.__values.popleft()

    def describe(self):
        """ Descriptive statistics for values collected. """
        return describe(self.__values, self.__name)

    def values(self):
        """ Returns copy of current values in the window. """
        return [x for x in self.__values]
