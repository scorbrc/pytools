import unittest
import datetime as dt
from random import randint, sample
from uuid import uuid4
from util.util_tools import (
    find_lcs,
    flatten_list,
    get_default,
    get_source_info,
    is_empty,
    is_list,
    is_num,
    to_camel_name,
    to_snake_name,
    to_str,
    zero_if_none
)


class UtilToolsTest(unittest.TestCase):

    def test_find_lcs_prefix(self):
        print("-- %s(%d): %s --" % get_source_info())
        common, unique = find_lcs(
            ['thefirstpart_abc', 'thefirstpart_def', 'thefirstpart_ghi'])
        self.assertEqual('thefirstpart_', common)
        self.assertEqual(['abc', 'def', 'ghi'], unique)

    def test_find_lcs_both_ends(self):
        print("-- %s(%d): %s --" % get_source_info())
        common, unique = find_lcs(
            ['before_abc_after', 'before_def_after', 'before_ghi_after'])
        self.assertEqual('before_', common)
        self.assertEqual(['abc_after', 'def_after', 'ghi_after'], unique)

    def test_find_lcs_middle(self):
        print("-- %s(%d): %s --" % get_source_info())
        name = str(uuid4())
        names = [str(uuid4()) + name + str(uuid4()) for _ in range(5)]
        common, unique = find_lcs(names)
        self.assertEqual(name, common)
        self.assertEqual(5, len(unique))
        self.assertEqual(72, len(unique[0]))

    def test_flatten_list(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual([1, 2, 3], flatten_list([1, 2, 3]))
        self.assertEqual([1, 2, 3, 4], flatten_list([[1, 2], [3, 4]]))
        self.assertEqual([1, 2, 3, 4, 5, {'no': 9}, 9],
                         flatten_list([[1, 2], [3, [4, 5]], {'no': 9}, [9]]))
        self.assertEqual([1, 2, 3, 4, 5],
                         flatten_list([[1, 2], [3, [4, 5], []]]))

    def test_get_default(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(None, get_default({}, 'x'))
        self.assertEqual(1, get_default({'x': 1}, 'x'))
        self.assertEqual('n', get_default({'x': 1}, 'y', 'n'))

    def test_get_source_info(self):
        print("-- %s(%d): %s --" % get_source_info())
        module, line_no, func = get_source_info()
        self.assertTrue('test_util_tools' in module)
        self.assertTrue(isinstance(line_no, int))
        self.assertEqual('test_get_source_info', func)

    def test_is_empty(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertTrue(is_empty(None))
        self.assertTrue(is_empty(''))
        self.assertTrue(is_empty([]))
        self.assertTrue(is_empty({}))
        self.assertFalse(is_empty(1))
        self.assertFalse(is_empty('a'))
        self.assertFalse(is_empty([1, 2, 3]))
        self.assertFalse(is_empty({1: 2}))
        self.assertTrue(is_empty({'a': 1, 'b': None}, 'c'))
        self.assertTrue(is_empty({'a': 1, 'b': None}, 'b'))

    def test_is_empty_k(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertTrue(is_empty({'a': 1}, 'b'))
        self.assertFalse(is_empty({'a': 1}, 'a'))

    def test_is_list(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertTrue(is_list([1, 2, 3]))
        self.assertFalse(is_list(1))

    def test_is_num(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertTrue(is_num(1))
        self.assertFalse(is_num('x'))
        self.assertFalse(is_num(None))
        self.assertTrue(is_num(1.2))

    def test_to_camel_name(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual('oneTwoThree', to_camel_name('one_two_three'))
        self.assertEqual('getHttpResponseCode',
                         to_camel_name('get_http_response_code'))

    def test_to_snake_name_1(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual('one_two_three', to_snake_name('OneTwoThree'))
        self.assertEqual('get_http_response_code',
                         to_snake_name('getHttpResponseCode'))

    def test_to_snake_name_2(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual("to_snake_name", to_snake_name("toSnakeName"))
        self.assertEqual("to_snake_name", to_snake_name("To_SnakeName"))
        self.assertEqual("_to_snake_name_", to_snake_name("_To_SnakeName__"))
        self.assertEqual("to_snake_name", to_snake_name("toSNAKEName"))

    def test_to_snake_name_and_back(self):
        print("-- %s(%d): %s --" % get_source_info())
        words = ["One", "Green", "Plus", "Forever", "Not",
                 "Blue", "Over", "Chain", "Four", "Bull", "Only"]
        names = [''.join(sample(words, k=randint(2, 4))) for _ in range(1000)]
        for name in names:
            cn1 = name[0].lower() + name[1:]
            sn1 = to_snake_name(cn1)
            cn2 = to_camel_name(sn1)
            self.assertEqual(cn1, cn2)

    def test_to_str(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual('1', to_str(1))
        self.assertEqual('1.2', to_str(1.234, digits=1))
        self.assertEqual('1.234', to_str(1.234))
        self.assertEqual('x', to_str('x'))
        self.assertEqual('', to_str(None))
        self.assertEqual('2020-01-01T15:30:11',
                         to_str(dt.datetime(2020, 1, 1, 15, 30, 11)))

    def test_zero_if_none(self):
        print("-- %s(%d): %s --" % get_source_info())
        self.assertEqual(1, zero_if_none(1))
        self.assertEqual(0, zero_if_none(None))
        self.assertEqual([1.2, 2.3, 3.4], zero_if_none([1.2, 2.3, 3.4]))
        self.assertEqual([1.2, 0, 3.4], zero_if_none([1.2, None, 3.4]))


if __name__ == '__main__':
    unittest.main()
