import unittest
import logging
from util.logging_utils import (
    create_file_handler,
    create_stream_handler,
    get_logger_info,
    get_logger,
    remove_handlers,
    setup_root_logger
)
from util.util_tools import get_source_info


class LoggingUtilsTest(unittest.TestCase):

    def test_create_file_handler(self):
        print("-- %s(%d): %s --" % get_source_info())
        fh = create_file_handler("log/app_name.log")
        self.assertTrue('RotatingFileHandler' in str(type(fh)))
        self.assertEqual(
            "%(asctime)s - %(levelname)s - p%(process)d " +
            "- t%(thread_id)d %(filename)s:%(lineno)d - %(message)s",
            fh.formatter._fmt)
        fh.close()

    def test_create_stream_handler(self):
        print("-- %s(%d): %s --" % get_source_info())
        sh = create_stream_handler(logging.INFO)
        self.assertTrue('StreamHandler' in str(type(sh)))
        self.assertEqual(
            '%(asctime)s - %(levelname)s - %(message)s',
            sh.formatter._fmt)

    def test_get_logger(self):
        print("-- %s(%d): %s --" % get_source_info())
        logger = get_logger()
        info = get_logger_info(logger)
        self.assertTrue('root' in info)
        self.assertEqual(0, len(info['root']['handlers']))

    def test_remove_root_logger_handlers(self):
        print("-- %s(%d): %s --" % get_source_info())
        setup_root_logger()
        info = get_logger_info()
        self.assertEqual(2, len(info['root']['handlers']))
        remove_handlers()
        info = get_logger_info()
        self.assertEqual(0, len(info['root']['handlers']))


if __name__ == '__main__':
    unittest.main()
