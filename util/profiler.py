""" A context class for profiling block of code and producing reports. """
import cProfile
from pstats import Stats
import io


class Profiler():
    """
    Context managed profiler used like:
    with Profiler() as pm:
        # Code to profile.
    print(pm)
    """
    def __init__(self):
        self.__pr = cProfile.Profile()
        self.__rpt = ''

    def __enter__(self):
        """ Start the profiler. """
        self.__pr.enable()
        return self

    def __exit__(self, *args):
        """ Stop the profile; collect stats. """
        self.__pr.disable()
        so = io.StringIO()
        ps = Stats(self.__pr, stream=so)
        ps.strip_dirs()
        ps.sort_stats('cumtime')
        ps.print_stats(.5)
        ps.print_callees(.5)
        self.__rpt = so.getvalue()

    def __str__(self):
        return self.__rpt
