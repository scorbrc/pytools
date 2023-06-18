import unittest
from random import choices, randint, random
import string
from util.rec_diff import rec_diff
from util.util_tools import get_source_info


def gen_obj():
    rn = randint(1, 3)
    if rn == 1:
        x = ''.join(choices(string.hexdigits, k=3))
    elif rn == 2:
        x = randint(100, 200)
    else:
        x = round(random() * 10)
    return {''.join(choices(string.hexdigits, k=5)): x}


class RecDiffTest(unittest.TestCase):

    def test_value_same(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', 'a', 'a')
        self.assertEqual(0, len(diffs))

    def test_value_different(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', 'a', 'b')
        self.assertEqual(1, len(diffs))
        self.assertEqual('changed', diffs[0].diff)

    def test_list_same(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', ['a', 'b', 'c'], ['a', 'b', 'c'])
        self.assertEqual(0, len(diffs))

    def test_list_value_different(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', ['a', 'b', 'c'], ['a', 'b', 'd'])
        self.assertEqual(2, len(diffs))
        self.assertEqual('removed', diffs[0].diff)
        self.assertEqual('added', diffs[1].diff)

    def test_list_type(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', ['a', 'b', 'c'], ['a', 'b', 1])
        self.assertEqual(1, len(diffs))
        self.assertEqual('type', diffs[0].diff)
        self.assertEqual('str', diffs[0].old)
        self.assertEqual('int', diffs[0].new)

    def test_multi_list_same(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', [['a', 'b'], ['c', 'd']], [
                         ['a', 'b'], ['c', 'd']])
        self.assertEqual(0, len(diffs))

    def test_multi_list_different(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', [['a', 'b'], ['c', 'd']], [
                         ['a', 'z'], ['c', 'd']])
        self.assertEqual(2, len(diffs))
        self.assertEqual('removed', diffs[0].diff)
        self.assertEqual('b', diffs[0].old)
        self.assertEqual(None, diffs[0].new)
        self.assertEqual('added', diffs[1].diff)
        self.assertEqual(None, diffs[1].old)
        self.assertEqual('z', diffs[1].new)

    def test_object_same(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', {'a': 1, 'b': 2}, {'a': 1, 'b': 2})
        self.assertEqual(0, len(diffs))

    def test_object_different(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', {'a': 1, 'b': 2}, {'a': 1, 'b': 3})
        self.assertEqual(1, len(diffs))
        self.assertEqual('changed', diffs[0].diff)
        self.assertEqual('new dict value changed', diffs[0].desc)
        self.assertEqual(2, diffs[0].old)
        self.assertEqual(3, diffs[0].new)

    def test_object_missing_key(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', {'a': 1, 'b': 2}, {'b': 2})
        self.assertEqual(1, len(diffs))
        self.assertEqual('root.a', diffs[0].key)
        self.assertEqual('removed', diffs[0].diff)
        self.assertEqual('old key not in new dict', diffs[0].desc)
        self.assertEqual(1, diffs[0].old)
        self.assertEqual(None, diffs[0].new)

    def test_object_extra_key(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', {9: 'a', 7: 'b'}, {9: 'a', 7: 'b', 'c': 3})
        self.assertEqual(1, len(diffs))
        self.assertEqual('root.c', diffs[0].key)
        self.assertEqual('added', diffs[0].diff)
        self.assertEqual('new key not in old dict', diffs[0].desc)
        self.assertEqual(None, diffs[0].old)
        self.assertEqual(3, diffs[0].new)

    def test_object_list_same(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', {'a': 1, 'b': [3, 4]}, {'a': 1, 'b': [3, 4]})
        self.assertEqual(0, len(diffs))

    def test_list_of_objects_same(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', [{'g': 1, 'b': 2}, {'c': 3, 'd': 4}],
                         [{'g': 1, 'b': 2}, {'c': 3, 'd': 4}])
        self.assertEqual(0, len(diffs))

    def test_list_of_objects_changed(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}],
                         [{'a': 1, 'b': 2}, {'c': 7, 'd': 4}])
        self.assertEqual(1, len(diffs))
        self.assertEqual('root.c', diffs[0].key)
        self.assertEqual('changed', diffs[0].diff)
        self.assertEqual('new dict value changed', diffs[0].desc)
        self.assertEqual(3, diffs[0].old)
        self.assertEqual(7, diffs[0].new)

    def test_list_of_objects_removed(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}],
                         [{'a': 1}, {'c': 3, 'd': 4}])
        self.assertEqual(1, len(diffs))
        self.assertEqual('root.b', diffs[0].key)
        self.assertEqual('removed', diffs[0].diff)
        self.assertEqual('old key not in new dict', diffs[0].desc)

    def test_list_of_objects_added(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', [{'a': 1, 'b': 2}, {'c': 3, 'd': 4}],
                         [{'a': 1, 'b': 2}, {'c': 3, 'd': 4, 'e': 5}])
        self.assertEqual(1, len(diffs))
        self.assertEqual('root.e', diffs[0].key)
        self.assertEqual('added', diffs[0].diff)
        self.assertEqual('new key not in old dict', diffs[0].desc)

    def test_object_exclusion(self):
        print("-- %s(%d): %s --" % get_source_info())
        diffs = rec_diff('root', [{'one': 1, 'two': 2}, {'three': 3, 'four': 4}],
                         [{'one': 1, 'two': 3}, {'three': 3}],
                         excls=('two', 'four'))
        self.assertEqual(0, len(diffs))

    def test_object_embedded(self):
        print("-- %s(%d): %s --" % get_source_info())
        old = [{'8d3C6': 9}, {'64CB4': 151}, {'sub1': {'69a5D': '9A4'},
                                              'sub2': {'d8F6C': 185}}]
        new = old
        diffs = rec_diff('root', old, new)
        self.assertEqual(0, len(diffs))

    def test_object_embedded_changed(self):
        print("-- %s(%d): %s --" % get_source_info())
        old = [{'8d3C6': 9}, {'64CB4': 151}, {'sub1': {'69a5D': '9A4'},
                                              'sub2': {'d8F6C': 185}}]
        new = [{'8d3C6': 9}, {'64CB4': 151}, {'sub1': {'69a5D': '9A4'},
                                              'sub2': {'d8F6C': 186}}]
        diffs = rec_diff('root', old, new)
        self.assertEqual(1, len(diffs))
        self.assertEqual('root.sub2.d8F6C', diffs[0].key)
        self.assertEqual('changed', diffs[0].diff)
        self.assertEqual('new dict value changed', diffs[0].desc)
        self.assertEqual(185, diffs[0].old)
        self.assertEqual(186, diffs[0].new)

    def test_object_embedded_double(self):
        print("-- %s(%d): %s --" % get_source_info())
        old = [{'6e1Ac': 157},
               {'80fae': 131},
               {'sub1': {'aEc89': 'e4a'},
                'sub2': [{'Ae9BD': 7},
                         {'c93f9': 135}]}]
        new = old
        diffs = rec_diff('root', old, new)
        self.assertEqual(0, len(diffs))

    def test_object_embedded_double_removed(self):
        print("-- %s(%d): %s --" % get_source_info())
        old = [{'6e1Ac': 157},
               {'80fae': 131},
               {'sub1': {'aEc89': 'e4a'},
                'sub2': [{'Ae9BD': 7},
                         {'c93f9': 135}]}]
        new = [{'6e1Ac': 157},
               {'80fae': 131},
               {'sub1': {'aEc89': 'e4a'},
                'sub2': [{'c93f9': 135}]}]
        diffs = rec_diff('root', old, new)
        self.assertEqual(2, len(diffs))
        self.assertEqual('root.sub2.Ae9BD', diffs[0].key)
        self.assertEqual('removed', diffs[0].diff)
        self.assertEqual('old key not in new dict', diffs[0].desc)
        self.assertEqual(7, diffs[0].old)
        self.assertEqual(None, diffs[0].new)
        self.assertEqual('root.sub2.c93f9', diffs[1].key)
        self.assertEqual('added', diffs[1].diff)
        self.assertEqual('new key not in old dict', diffs[1].desc)
        self.assertEqual(None, diffs[1].old)
        self.assertEqual(135, diffs[1].new)


if __name__ == '__main__':
    unittest.main()
