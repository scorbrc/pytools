""" Contect class for timing blocks of code. """
from logging import Logger
from time import perf_counter


class Timer():

    def __init__(self, *args):
        """
        Create a timer with optional 'args' that may have a string name and
        a Logger to write timer report to after exiting.
        """
        self.name = "Timer"
        self.log = None
        for arg in args:
            if isinstance(arg, str):
                self.name = arg
            elif isinstance(arg, Logger):
                self.log = arg
            else:
                raise ValueError("Invalid argument: %s" % arg)
        self.__st = 0
        self.__secs = 0

    def __enter__(self):
        """ Start the timer. """
        self.__st = perf_counter()
        return self

    def __exit__(self, *args):
        """ Stop the timer; post the results. """
        self.__secs = perf_counter() - self.__st
        if self.log is not None:
            self.log.info(self)

    @property
    def millis(self):
        """ The elapsed time in milliseconds. """
        return self.__secs * 1000

    @property
    def secs(self):
        """ The elapsed time in seconds. """
        return self.__secs

    def __str__(self):
        return "%s: Elapsed secs: %.3f" % (self.name, self.__secs)
