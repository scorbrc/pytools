import unittest
import inspect
import os
from time import sleep
from util.timer import Timer
from util.util_tools import get_logger


class TimerTest(unittest.TestCase):

    def test_timer(self):
        print('-- %s --' % inspect.stack()[0][3])
        with Timer() as tm:
            sleep(.5)
        self.assertTrue(tm.secs >= .5)

    def test_timer_name_arg(self):
        print('-- %s --' % inspect.stack()[0][3])
        with Timer("test") as tm:
            self.assertEqual("test", tm.name)

    def test_timer_logger_arg(self):
        print('-- %s --' % inspect.stack()[0][3])
        logger = get_logger('timer_logger_arg')
        with Timer(logger, "test_log") as tm:
            sleep(.5)
        with open('log/timer_logger_arg.log') as fi:
            content = fi.read()
            os.remove('log/timer_logger_arg.log')
        self.assertEqual("test_log", tm.name)
        self.assertTrue(str(tm) in content)

if __name__ == '__main__':
    unittest.main()
