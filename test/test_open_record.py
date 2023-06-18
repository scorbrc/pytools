import unittest
import csv
import datetime as dt
import io
import json
from random import choice, choices, shuffle
import string
from util.open_record import OpenRecord
from util.util_tools import get_source_info


def random_b36(n_chars):
    """ Generate random base 62 string 'n_chars' characters long, """
    return ''.join(choices(string.digits + string.ascii_uppercase, k=n_chars))


class OpenRecordTest(unittest.TestCase):

    def test_construct_fields(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(foo=456, bar='def')
        self.assertTrue(rec.foo == 456)
        self.assertTrue(rec.bar == 'def')

    def test_construct_pairs(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(zip(['a', 'b', 'c'], [1, 'x', 3.21]))
        self.assertTrue(rec.a == 1)
        self.assertTrue(rec.b == 'x')
        self.assertTrue(rec.c == 3.21)

    def test_add_method(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(name='add_a_method')

        def xdata(self):
            return [1, 2, 3]
        rec.add_method(xdata, 'data')
        self.assertEqual([1, 2, 3], rec.data())

    def test_csv(self):
        print("-- %s(%d): %s --" % get_source_info())
        so = io.StringIO()
        wt = csv.writer(so)
        cd = dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        for a, b, c in (('f1', 'f2', 'f3'),
                        ('x', cd, 1),
                        ('y', cd, 2),
                        ('y', cd, 3)):
            wt.writerow((a, b, c))
        x = so.getvalue()
        recs = list(OpenRecord.create_from_csv(io.StringIO(x)))
        self.assertEqual(3, len(recs))
        self.assertEqual('x', recs[0].f1)
        self.assertEqual(cd, recs[1].f2)
        self.assertEqual('3', recs[2].f3)

    def test_dict_1(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec1 = OpenRecord(a=1, b=2.1)
        rec2 = rec1.copy()
        rec1.b = 3.4
        self.assertEqual(2.1, rec2.b)
        self.assertEqual(3.4, rec1.b)

    def test_dict_2(self):
        print("-- %s(%d): %s --" % get_source_info())
        r1 = OpenRecord(n1='abc')
        r1.embedded = OpenRecord(n2='123', a=1, b=2, c=3)
        r1.details = ['abc', 'str', OpenRecord(n3='123', z=-1), 0, 1.2]
        r1.created_at = 'abc'
        d1 = json.dumps(r1)
        r2 = OpenRecord(json.loads(d1))
        d2 = json.dumps(r2)
        self.assertEqual(len(d1), len(d2))
        self.assertEqual(r1['n1'], r2['n1'])
        self.assertEqual(r1['created_at'], r2['created_at'])
        self.assertEqual(len(r1['details']), len(r2['details']))

    def test_dict_values(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(a=1, b=2, c=[1, 2, 3],
                         sr=OpenRecord(x=1, y=2, z=[1, 2, 3]))
        self.assertEqual(1, rec.a, str(rec))
        self.assertEqual(2, rec.sr.y, str(rec))

    def test_embedded(self):
        print("-- %s(%d): %s --" % get_source_info())
        dd = {'name': 'the_name',
              'a': 1,
              'b': {'first': 'last',
                      'date': dt.datetime.now(),
                      'x': 1.23,
                      'y': {'a': 1,
                            'b': 2}},
              'c': 3}
        rec = OpenRecord(dd)
        self.assertTrue(isinstance(rec.b, OpenRecord))
        self.assertTrue(isinstance(rec.b.y, OpenRecord))

    def test_equals(self):
        print("-- %s(%d): %s --" % get_source_info())
        r1 = OpenRecord(a='one', b='two')
        r2 = OpenRecord(r1)
        self.assertTrue(r1 == r2)
        r2.c = 'three'
        self.assertFalse(r1 == r2)

    def test_field_count(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(a=1, b=2, c=3)
        self.assertEqual(3, len(rec.values()))

    def test_fields(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord()
        rec.foo = 123
        self.assertTrue(rec.foo == 123)
        rec.bar = 'abc'
        self.assertTrue(rec.bar == 'abc')
        self.assertTrue(list(rec.values()) == [123, 'abc'])
        rec.bar = 'xyz'
        self.assertTrue(list(rec.values()) == [123, 'xyz'])

    def test_keys(self):
        print("-- %s(%d): %s --" % get_source_info())
        # OpenRecords will be ordered by 'a' if key 'k' not defined.
        recs1 = []
        for i in range(5):
            rec = OpenRecord(a=9 - i, k=i, b=choice(string.ascii_lowercase))
            recs1.append(rec)
        shuffle(recs1)
        last_k = None
        for rec in sorted(recs1):
            if last_k is not None:
                self.assertTrue(rec.k < last_k, "Expected k to be decreasing")
            last_k = rec.k
        recs1 = []
        for i in range(5):
            rec = OpenRecord(a=9 - i, k=i, b=choice(string.ascii_lowercase))
            rec.add_key('k')
            recs1.append(rec)
        shuffle(recs1)
        last_k = None
        for rec in sorted(recs1):
            if last_k is not None:
                self.assertTrue(rec.k > last_k, "Expected k to be increasing")
            last_k = rec.k

    def test_repr_01(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(a='one',
                         b={'first': 1, 'second': 2},
                         c=[{'x': 'one', 'y': 'two'}, {'z': 'three'}])
        exp = "{a=one,b={first=1,second=2},c=[{x=one,y=two},{z=three}]}"
        self.assertEqual(exp, repr(rec), rec)

    def test_repr_02(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord({
            "audience": [
                "eventing"
            ],
            "iss": "SSE",
            "alg": "rs256"
        })
        exp = "{alg=rs256,audience=[eventing],iss=SSE}"
        self.assertEqual(exp, repr(rec), rec)

    def test_hash(self):
        print("-- %s(%d): %s --" % get_source_info())
        r1 = OpenRecord(a='one', b='two')
        r2 = OpenRecord(r1)
        self.assertTrue(hash(r1) == hash(r2))
        r2.c = 'three'
        self.assertFalse(hash(r1) == hash(r2))

    def test_json(self):
        print("-- %s(%d): %s --" % get_source_info())
        js = '{"a":1,"b":2.31,"c":[1,2,3]}'
        rec = OpenRecord.create_from_json(js)
        self.assertTrue('a' in rec)
        self.assertTrue('b' in rec)
        self.assertTrue('c' in rec)
        self.assertEqual(1, rec.a)
        self.assertEqual(2.31, rec.b)
        self.assertEqual([1, 2, 3], rec.c)

    def test_json_array(self):
        print("-- %s(%d): %s --" % get_source_info())
        js = '[{"a":1,"b":"x","c":[1,2,3]},{"a":2,"b":"y","c":[1,2,3]}]'
        for x in (js, io.StringIO(js)):
            recs = list(OpenRecord.create_from_json(x))
            self.assertEqual(2, len(recs))
            self.assertTrue('a' in recs[0])
            self.assertTrue('b' in recs[0])
            self.assertTrue('c' in recs[0])
            self.assertEqual(1, recs[0].a)
            self.assertEqual('x', recs[0].b, 1)
            self.assertEqual([1, 2, 3], recs[0].c)
            self.assertTrue('a' in recs[1])
            self.assertTrue('b' in recs[1])
            self.assertTrue('c' in recs[1])
            self.assertEqual(2, recs[1].a)
            self.assertEqual('y', recs[1].b, 1)
            self.assertEqual([1, 2, 3], recs[1].c)

    def test_order(self):
        print("-- %s(%d): %s --" % get_source_info())
        d1 = dt.datetime.now() - dt.timedelta(days=1)
        d2 = dt.datetime.now() - dt.timedelta(days=2)
        d3 = dt.datetime.now() - dt.timedelta(days=3)
        recs = [OpenRecord(a=1, b='x', c=d2),
                OpenRecord(a=2, b='x', c=d1),
                OpenRecord(a=1, b='x', c=d1),
                OpenRecord(a=1, b='x', c=d3),
                OpenRecord(a=1, b='z', c=d1)]
        srecs = sorted(recs)
        self.assertTrue(srecs[0].a == 1 and srecs[0].b ==
                        'x' and srecs[0].c == d3)
        self.assertTrue(srecs[1].a == 1 and srecs[1].b ==
                        'x' and srecs[1].c == d2)
        self.assertTrue(srecs[2].a == 1 and srecs[2].b ==
                        'x' and srecs[2].c == d1)
        self.assertTrue(srecs[3].a == 1 and srecs[3].b ==
                        'z' and srecs[3].c == d1)
        self.assertTrue(srecs[4].a == 2 and srecs[4].b ==
                        'x' and srecs[4].c == d1)

    def test_repr(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(a='x',
                         b={'first': 1, 'second': 2},
                         c=[{'x': 'one', 'y': 'two'}, {'z': 'three'}])
        self.assertEqual(
            '{a=x,b={first=1,second=2},c=[{x=one,y=two},{z=three}]}', repr(rec))

    def test_select(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec1 = OpenRecord(a=1, b=2, c=3)
        rec2 = rec1.select(('a', 'c'))
        self.assertTrue('a' in rec2)
        self.assertEqual(rec2.a, 1)
        self.assertFalse('b' in rec2)
        self.assertTrue('c' in rec2)
        self.assertEqual(rec2.c, 3)

    def test_values(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord((('a', 1), ('b', 2), ('c', 3)))
        self.assertEqual(3, len(rec.values()))
        values = list(rec.values())
        self.assertEqual(1, values[0])
        self.assertEqual(2, values[1])
        self.assertEqual(3, values[2])

    def test_text_by_rows(self):
        print("-- %s(%d): %s --" % get_source_info())
        recs = [OpenRecord(name='first',
                           value1=1.23,
                           value2=456,
                           date=dt.datetime.now()),
                OpenRecord(name='second',
                           value1=1.23,
                           value2=456,
                           date=dt.datetime.now()),
                OpenRecord(name='the third longer name',
                           value1=1.23,
                           value2=456,
                           date=dt.datetime.now())]
        content = OpenRecord.to_text_rows(recs)
        self.assertEqual(4, len(content.split('\n')), content)
        self.assertEqual(4, len(content.split('\n')[0].split()), content)

    def test_text_by_cols(self):
        print("-- %s(%d): %s --" % get_source_info())
        recs = [OpenRecord(name='first',
                           value1=1.23,
                           value2=456,
                           date=dt.datetime.now()),
                OpenRecord(name='second',
                           value1=1.23,
                           value2=456,
                           date=dt.datetime.now()),
                OpenRecord(name='the third longer name',
                           value1=1.23,
                           value2=456,
                           date=dt.datetime.now())]
        content = OpenRecord.to_text_cols(recs)
        self.assertEqual(4, len(content.split('\n')), content)
        self.assertEqual(4, len(content.split('\n')[1].split()), content)

    def test_text_by_cols_embedded(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(
            name='first',
            date=dt.datetime.now(),
            value1=1.23,
            value2=456,
            subs=OpenRecord(a=1, b=2))
        self.assertEqual(1, rec.subs.a)

    def test_text_digits(self):
        print("-- %s(%d): %s --" % get_source_info())
        rec = OpenRecord(a=1.23456, b=2.79797979)
        rpt = OpenRecord.to_text_cols(rec)
        for i, x in enumerate(rpt.split('\n')):
            d = x.split()[-1].partition('.')[2]
            self.assertEqual(3, len(d))
            if i == 0:
                self.assertEqual('235', d)
            elif i == 1:
                self.assertEqual('798', d)

    def test_text_max_len(self):
        print("-- %s(%d): %s --" % get_source_info())
        recs = []
        for i in range(3):
            recs.append(
                OpenRecord(
                    a=random_b36(30),
                    b=random_b36(10 if i != 2 else 50)))
        rpt = OpenRecord.to_text_rows(recs, max_len=40)
        for line in rpt.split('\n'):
            for fld in line.split():
                self.assertTrue(len(fld) <= 40)


if __name__ == '__main__':
    unittest.main()
