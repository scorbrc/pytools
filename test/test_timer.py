import unittest
import logging
import os
from time import sleep
from util.timer import Timer
from util.logging_utils import get_logger, get_logger_info
from util.random_utils import RandomUtils
from util.util_tools import get_source_info


class TimerTest(unittest.TestCase):

    def test_timer(self):
        print("-- %s(%d): %s --" % get_source_info())
        with Timer() as tm:
            sleep(.5)
        self.assertTrue(tm.secs >= .5)

    def test_timer_name_arg(self):
        print("-- %s(%d): %s --" % get_source_info())
        with Timer("test") as tm:
            self.assertEqual("test", tm.name)

    def test_timer_logger_arg(self):
        print("-- %s(%d): %s --" % get_source_info())
        ru = RandomUtils()
        app_name = ru.b36(10)
        #print(get_logger_info())
        logger = get_logger(app_name, file_dir='log')
        logger.info("test_timer_logger_arg")
        for _ in range(3):
            with Timer(logger, "test_log") as tm:
                sleep(.05)
        fp = 'log/%s.log' % app_name
        with open(fp) as fi:
            content = fi.read()
            #os.remove(fp)
        self.assertEqual("test_log", tm.name)
        self.assertTrue(str(tm) in content)


if __name__ == '__main__':
    unittest.main()
