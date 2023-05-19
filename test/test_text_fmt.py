import unittest
from collections import OrderedDict
import datetime as dt

import inspect
from util.text_fmt import format_text_table


class TextFmtTest(unittest.TestCase):

    def test_format_text_table_horizontal(self):
        print('-' * 80)
        print(inspect.stack()[0][3])
        recs = [OrderedDict(name='first',
                            value1=1.23,
                            value2=456,
                            date=dt.datetime.now()),
                OrderedDict(name='second',
                            value1=1.23,
                            value2=456,
                            date=dt.datetime.now()),
                OrderedDict(name='the third longer name',
                            value1=1.23,
                            value2=456,
                            date=dt.datetime.now())]
        content = format_text_table(recs)
        self.assertEqual(4, len(content.split('\n')), content)
        self.assertEqual(4, len(content.split('\n')[0].split()), content)

    def test_format_text_table_vertical(self):
        print('-' * 80)
        print(inspect.stack()[0][3])
        recs = [OrderedDict(name='first',
                            value1=1.23,
                            value2=456,
                            date=dt.datetime.now()),
                OrderedDict(name='second',
                            value1=1.23,
                            value2=456,
                            date=dt.datetime.now()),
                OrderedDict(name='the third longer name',
                            value1=1.23,
                            value2=456,
                            date=dt.datetime.now())]
        content = format_text_table(recs,
                                    by_cols=True,
                                    colnames=('1', '2', '3'))
        self.assertEqual(5, len(content.split('\n')), content)
        self.assertEqual(3, len(content.split('\n')[0].split()), content)


if __name__ == '__main__':
    unittest.main()
