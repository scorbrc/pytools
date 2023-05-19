import unittest
import inspect
import json
import logging
from util.logging_utils import (
    create_file_handler,
    create_stream_handler,
    get_default_app_name,
    get_logger_info,
    get_logger,
    remove_handlers,
    setup_root_logger
)


class LoggingUtilsTest(unittest.TestCase):

    def test_create_file_handler(self):
        print('-- %s --' % inspect.stack()[0][3])
        fh = create_file_handler("log/app_name.log")
        self.assertTrue('RotatingFileHandler' in str(type(fh)))
        self.assertEqual(
            "%(asctime)s - %(levelname)s - p%(process)d " + \
            "- t%(thread_id)d %(filename)s:%(lineno)d - %(message)s",
            fh.formatter._fmt)

    def test_create_stream_handler(self):
        print('-- %s --' % inspect.stack()[0][3])
        sh = create_stream_handler(logging.INFO)
        self.assertTrue('StreamHandler' in str(type(sh)))
        self.assertEqual('%(asctime)s - %(levelname)s - %(message)s', sh.formatter._fmt)

    def test_get_default_app_name(self):
        print('-- %s --' % inspect.stack()[0][3])
        self.assertEqual('filename', get_default_app_name('filename'))
        self.assertEqual('test_logging_utils', get_default_app_name())

    def test_get_logger(self):
        print('-- %s --' % inspect.stack()[0][3])
        logger = get_logger()
        info = get_logger_info(logger)
        self.assertTrue('root' in info)
        self.assertEqual(0, len(info['root']['handlers']))
        self.assertTrue('test_logging_utils' in info)
        self.assertEqual(2, len(info['test_logging_utils']['handlers']))

    def test_remove_root_logger_handlers(self):
        print('-- %s --' % inspect.stack()[0][3])
        setup_root_logger()
        info = get_logger_info()
        self.assertEqual(2, len(info['root']['handlers']))
        remove_handlers()
        info = get_logger_info()
        self.assertEqual(0, len(info['root']['handlers']))


if __name__ == '__main__':
    unittest.main()
