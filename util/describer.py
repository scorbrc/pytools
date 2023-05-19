from collections import deque
from util.stat_utils import describe

MAX_VALUES = 50000

class Describer:
    """
    Collected values for descriptive statistics.
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
