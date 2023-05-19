from random import choice
import string
from time import time
from .random_utils import (
    int_to_b62,
    random_b62
)

class ShortUID:
    """
    Generates 11 charcter short UID's with four components:
    1) Base 62 series character provided by the client.
    2) Random three base 62 characters and so with 238328 possible values.
    3) Epoch 10th of a second that rolls over every 1060 days. This allows
    epoch seconds to be stored in five base 62 characters.
    4) Sequential number that rolls over at 238327. This allows sequential
    numbers to be stored in three base 62 characters.
    """
    MAX_SECS = 62**5 - 1
    MAX_SEQ = 62**3 - 1

    def __init__(self, series='x'):
        if len(series) > 1:
            raise ValueError("Series must be one character.")
        self.__series = str(series)
        self.__sequence = 0

    def next(self):
        rchr = random_b62(3)
        rsec = int_to_b62(int(time()*10) % ShortUID.MAX_SECS).rjust(5, '0')
        rseq = int_to_b62(self.__sequence % ShortUID.MAX_SEQ).rjust(3, '0')
        self.__sequence += 1
        return ''.join((self.__series, rchr, rsec, rseq))
