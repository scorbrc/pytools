#!/usr/bin/env python3
"""
Examines records and fields to characterize the types of characters and values.
"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import defaultdict
import concurrent.futures as cf
import csv
from decimal import Decimal
from fnmatch import fnmatch
import io
import json
from math import sqrt
from multiprocessing import cpu_count
import numpy as np
import scipy.stats as ss
import os
import string
import sys
from util.time_utils import to_utc
from util.util_tools import get_type, max_or_none, min_or_none

DIGITS = 3
MAX_COLLECT = 1000000
MAX_UNIQUES = 50000
MAX_SHOW = 50
MAX_SIZE = 40
MIN_UNIQ = 2
MULTI_PROC_H = 500000


class Field:
    """ A Field to characterize. """

    def __init__(self, name, **kv_args):
        """
        Create Field with key word arguments:
        name is the field name
        orig_type is the original set of character types.
        conv_types is the converted set of character types.
        count is number of values found in the field.
        missing is number of missing values.
        values are the unique values and counts, up to MAX_UNIQUES.
        chars is used to accumulate the types of characters.
        """
        self.__name = name
        self.__digits = kv_args.get('digits', DIGITS)
        self.__max_collect = kv_args.get('max_collect', MAX_COLLECT)
        self.__max_uniques = kv_args.get('max_uniques', MAX_UNIQUES)
        self.__max_show = kv_args.get('max_show', MAX_SHOW)
        self.__max_size = kv_args.get('max_size', MAX_SIZE)
        self.__orig_types = set(kv_args.get('orig_types', []))
        self.__conv_types = set(kv_args.get('conv_types', []))
        self.__min_len = kv_args.get('min_len', None)
        self.__max_len = kv_args.get('max_len', None)
        self.__min_val = kv_args.get('min_val', None)
        self.__max_val = kv_args.get('max_val', None)
        self.__count = kv_args.get('count', 0)
        self.__missing = kv_args.get('missing', 0)
        self.__values = kv_args.get('values', defaultdict(int))
        self.__data = kv_args.get('data', [])
        if 'chars' in kv_args:
            self.__chars = kv_args['chars']
        else:
            self.__chars = {}

    def describe(self):
        """ Descriptive statistics for data collected. """
        pcts = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)
        ds = dict(name=self.__name, n=len(self.__data), mu=0, sd=0)
        for pc in pcts:
            ds['p%02d' % pc] = 0
        if len(self.__data) >= 3:
            ds['mu'] = np.mean(self.__data)
            ds['sd'] = np.std(self.__data)
            for pc, pv in zip(pcts, np.percentile(self.__data, pcts)):
                ds['p%02d' % pc] = pv
        return ds

    def evaluate(self, val):
        """ Characterize string 'val'. """
        if val is None:
            self.__count += 1
            self.__missing += 1
        elif isinstance(val, Field):
            # Value is a field, aggregate into this Field.
            self.__digits = val.__digits
            self.__max_collect = val.__max_collect
            self.__max_uniques = val.__max_uniques
            self.__max_show = val.__max_show
            self.__max_size = val.__max_size
            self.__orig_types.update(val.__orig_types)
            self.__conv_types.update(val.__conv_types)
            self.__min_len = min_or_none(self.__min_len, val.__min_len)
            self.__max_len = max_or_none(self.__max_len, val.__max_len)
            self.__min_val = min_or_none(self.__min_val, val.__min_val)
            self.__max_val = max_or_none(self.__max_val, val.__max_val)
            self.__count += val.__count
            self.__missing += val.__missing
            for v, c in val.__values.items():
                if len(self.__values) < self.__max_uniques:
                    self.__values[v] += c
            self.__chars.update(val.__chars)
            space = self.__max_collect - len(self.__data)
            if space < len(val.__data):
                self.__data = self.__data[len(val.__data) - space:]
            self.__data.extend(val.__data)
        else:
            # Add a value to this field.
            self.__count += 1
            conv_val = val
            conv_type = get_type(val)
            self.__orig_types.add(get_type(val))
            if isinstance(val, str):
                # Input type is string.
                val = val.strip()
                if not len(val):
                    self.__missing += 1
                else:
                    for c in val:
                        if c.isalpha():
                            if c.islower():
                                self.__chars["a-z"] = string.ascii_lowercase
                            else:
                                self.__chars["A-Z"] = string.ascii_uppercase
                        elif c.isdigit():
                            self.__chars["0-9"] = string.digits
                        elif c.isspace():
                            self.__chars["space"] = ' '
                        elif c.isprintable():
                            self.__chars['special'] = string.punctuation
                        else:
                            self.__chars["ctrl"] = ''
                    conv_val = val
                    conv_type = 'str'
                    try:
                        conv_val = int(val)
                        conv_type = 'int'
                    except BaseException:
                        try:
                            conv_val = float(val)
                            conv_type = 'float'
                        except BaseException:
                            if len(val) >= 10 and len(val) <= 30:
                                if len([v for v in val if v.isdigit()]) >= 8:
                                    if len([v for v in val if v in "-/, "]) >= 2:
                                        try:
                                            dx = to_utc(val)
                                            if dx is not None:
                                                conv_val = dx
                                                conv_type = 'datetime'
                                        except BaseException:
                                            pass
                    if conv_type == 'str':
                        self.__min_len = \
                            min_or_none(self.__min_len, len(conv_val))
                        self.__max_len = \
                            max_or_none(self.__max_len, len(conv_val))
                    elif conv_type == 'datetime':
                        self.__min_val = min_or_none(self.__min_val, conv_val)
                        self.__max_val = max_or_none(self.__max_val, conv_val)
                    self.__conv_types.add(conv_type)
            elif isinstance(val, (float, Decimal)):
                val = ("%%.%df" % DIGITS) % float(val)
                conv_type = 'float'
            elif isinstance(val, int):
                val = str(val)
                conv_type = 'int'
            else:
                conv_type = get_type(val)
                val = str(val)
            self.__orig_types.add(get_type(val))
            self.__conv_types.add(conv_type)
            if conv_type == 'str' or conv_type == 'datetime':
                if len(val) and len(val) <= self.__max_size:
                    if len(self.__values) < self.__max_uniques:
                        self.__values[val] += 1
            elif conv_type == 'float' or conv_type == 'int':
                if len(self.__data) > self.__max_collect * 1.05:
                    self.__data = self.__data[int(
                        self.__max_collect * .05):]
                self.__data.append(conv_val)

    def get_chars(self):
        """ Character types found in the field. """
        return list(self.__chars.keys())

    def get_conv_types(self):
        return sorted(list(self.__conv_types))

    def get_count(self):
        """ Number of values found. """
        return self.__count

    def get_data(self):
        """ Returns copy of numeric values. """
        return [x for x in self.__data]

    def get_max_len(self):
        """ Maximim length of string field. """
        return self.__max_len

    def get_min_len(self):
        """ Minimum length of string field. """
        return self.__min_len

    def get_name(self):
        """ Field name. """
        return self.__name

    def get_orig_types(self):
        return sorted(list(self.__orig_types))

    def get_unique_count(self):
        """ Number of unique values found. """
        return len(self.__values)

    def is_numeric(self):
        """ Indicates it field is numeric. """
        return 'float' in self.__conv_types or 'int' in self.__conv_types

    def probs(self):
        """ Probability of each unique value occurring. """
        s = sum(self.__values.values())
        xcs = sorted(self.__values.items(), key=lambda xc: xc[1], reverse=True)
        return [(x, c / s) for x, c in xcs]

    def values(self):
        """ Unique values found in the field. """
        for x, c in self.__values.items():
            for _ in range(c):
                yield x

    def report(self):
        """ Generate a report for the field. """
        so = io.StringIO()
        print("%s:" % self.__name, file=so)
        print("  %d values" % self.__count, file=so)
        if len(self.__values):
            print("  %d distinct values" % len(self.__values), file=so)
        elif len(self.__data):
            print("  %d distinct values" % len(set(self.__data)), file=so)
        print("  %d missing" % self.__missing, file=so)
        if len(self.__chars):
            print("  Chars: %s" % ','.join(self.__chars), file=so)
        if self.__orig_types == self.__conv_types:
            print("  Types: %s" %
                  ','.join(sorted(list(self.__orig_types))), file=so)
        else:
            print("  Orig types: %s" %
                  ','.join(sorted(list(self.__orig_types))), file=so)
            print("  Conv types: %s" %
                  ','.join(sorted(list(self.__conv_types))), file=so)
        if self.__min_len is not None and self.__max_len is not None:
            print("  Minimum length: %d, maximum length: %d" %
                  (self.__min_len, self.__max_len), file=so)
        if self.__min_val is not None and self.__max_val is not None:
            print("  Minimum: %s, maximum: %s" %
                  (self.__min_val.isoformat()[:19],
                   self.__max_val.isoformat()[:19]),
                  file=so)
        if len(self.__values) >= MIN_UNIQ:
            # Show top values for string field.
            print("  Top %d values:" %
                  min(self.__max_show, len(self.__values)), file=so)
            max_len = max([len(x) for x in self.__values])
            values = sorted(
                self.__values.items(), key=lambda xc: xc[1], reverse=True)
            for i, (x, c) in enumerate(values):
                print("    %s : %d" % (x.ljust(max_len), c), file=so)
                if i == self.__max_show:
                    break
        elif len(self.__data) >= 3:
            # Show descriptive statistics for numeric field.
            print("  Description:", file=so)
            fmt = '    %%-4s : %%.%df' % self.__digits
            for fn, fv in self.describe().items():
                if fn != 'name':
                    print(fmt % (fn, fv), file=so)
        return so.getvalue()

    def to_dict(self):
        return dict(
            name=self.__name,
            digits=self.__digits,
            max_collect=self.__max_collect,
            max_uniques=self.__max_uniques,
            max_show=self.__max_show,
            max_size=self.__max_size,
            orig_types=self.__orig_types,
            conv_types=self.__conv_types,
            min_len=self.__min_len,
            max_len=self.__max_len,
            min_val=self.__min_val,
            max_val=self.__max_val,
            count=self.__count,
            missing=self.__missing,
            values=self.__values,
            chars=self.__chars
        )

    def __str__(self):
        return self.report()


def analyze(kv_args, records):
    """ Characterize each record in 'records'. """
    fcs = {}
    for rec in records:
        if rec is not None:
            _analyze_rec_(kv_args, fcs, rec)
    return fcs


def _analyze_rec_(kv_args, fcs, rec, qual=None):
    """ Characterize 'rec' with list of fields 'fcs' and name qualifier 'qual'. """
    for fn, fv in rec.items():
        if isinstance(fv, dict):
            _analyze_rec_(kv_args, fcs, fv, fn)
        else:
            name = "%s.%s" % (qual, fn) if qual is not None else fn
            fcs.setdefault(name, Field(name, **kv_args))
            fcs[name].evaluate(fv)


class FieldChars:
    """
    Characterizes records and fields from list, dictionary,
    JSON string of CSV file.
    """

    def __init__(self, src, fields):
        self.__source = src
        self.__fields = fields

    @staticmethod
    def evaluate(src, **kv_args):
        records = []
        if isinstance(src, (list, tuple)):
            records = src
        elif isinstance(src, str):
            if os.path.exists(src):
                if src.endswith('.json'):
                    with open(src) as fi:
                        records = json.load(fi)
                else:
                    sniffer = csv.Sniffer()
                    with open(src) as fi:
                        sample = fi.read(4096)
                    with open(src) as fi:
                        dialect = sniffer.sniff(sample)
                        for rec in csv.DictReader(fi, dialect=dialect):
                            records.append(rec)
            else:
                try:
                    records = json.loads(src)
                except Exception as ex:
                    raise ValueError("failed to parse %s: %s" % (src[:40], ex))

        if not len(records):
            raise ValueError("No data to evaluate.")
        if 'select' in kv_args and kv_args['select'] is not None:
            sel_fn = eval(kv_args['select'])
            records = [rec for rec in records if sel_fn(rec)]
        if 'fields' in kv_args and kv_args['fields'] is not None:
            if len(kv_args['fields']):
                fld_names = set()
                for fn in records[0]:
                    for fe in kv_args['fields']:
                        if fnmatch(fn, fe):
                            fld_names.add(fn)
                sel_recs = []
                for rec in records:
                    sel_recs.append(
                        {fn: fv for fn, fv in rec.items() if fn in fld_names})
                records = sel_recs

        if len(records) * len(records[0]) < MULTI_PROC_H:
            fcs = {fn: fld for fn, fld in analyze(kv_args, records).items()}
            return FieldChars(src, fcs)

        fcs = {}
        procs_n = cpu_count() // 2 + 1
        chunk_n = int(sqrt(len(records) / sqrt(procs_n)))
        with cf.ProcessPoolExecutor(max_workers=procs_n) as executor:
            futures = set()
            for i in range(0, len(records), chunk_n):
                ft = executor.submit(analyze, kv_args, records[i:i + chunk_n])
                futures.add(ft)
            try:
                for ft in cf.as_completed(futures):
                    if ft.exception() is not None:
                        raise ft.exception()
                    fc = ft.result()
                    for fn, fld in fc.items():
                        if fn is not None:
                            try:
                                fcs[fn].evaluate(fld)
                            except KeyError:
                                fcs[fn] = Field(fn)
                                fcs[fn].evaluate(fld)
            except KeyboardInterrupt:
                print('Terminating...')
                sys.exit(1)
        return FieldChars(src, fcs)

    def get_fields(self):
        return self.__fields

    def report(self, max_show=100, corr=False):
        so = io.StringIO()
        for name in sorted(self.__fields):
            print(self.__fields[name], file=so)
        if corr:
            num_flds = [fld for fld in self.__fields.values()
                        if fld.is_numeric()]
            max_len = max([len(fld.get_name()) for fld in num_flds])
            if len(num_flds):
                print("\n%s %s %8s %8s" %
                      ('x'.ljust(max_len), 'y'.ljust(max_len), 'cr', 'pv'),
                      file=so)
                cr_recs = []
                for i in range(len(num_flds) - 1):
                    for j in range(i + 1, len(num_flds)):
                        cr, pv = ss.spearmanr(
                            num_flds[i].get_data(), num_flds[j].get_data())
                        if pv < .01:
                            cr_recs.append(dict(x=num_flds[i].get_name(),
                                                y=num_flds[j].get_name(),
                                                cr=cr,
                                                pv=pv))
                for cr_rec in sorted(cr_recs,
                                     key=lambda cr: abs(cr['cr']),
                                     reverse=True):
                    print("%s %s %8.4f %8.4f" %
                          (cr_rec['x'].ljust(max_len),
                           cr_rec['y'].ljust(max_len),
                           cr_rec['cr'],
                           cr_rec['pv']),
                          file=so)
        return so.getvalue()

    def to_dict(self):
        return dict(source=self.__source,
                    fields=[fld.to_dict() for fld in self.__fields])


if __name__ == '__main__':

    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'file',
        help="CSV file to analyze.")
    parser.add_argument(
        '--fields',
        nargs='+',
        help="List of field name or field name wildcard expressions to select.")
    parser.add_argument(
        '--corr',
        action='store_true',
        help="Correlations between numeric fields.")
    parser.add_argument(
        '--digits',
        type=int,
        default=DIGITS,
        help="Digits to the right of point to display.")
    parser.add_argument(
        '--max-collect',
        dest='MAX_UNIQUES',
        type=int,
        default=MAX_UNIQUES,
        help="Maximum unique values to collect.")
    parser.add_argument(
        '--max-show',
        dest='max_show',
        type=int,
        default=MAX_SHOW,
        help="Maximum unique values to show in report.")
    parser.add_argument(
        '--max-size',
        dest='max_size',
        type=int,
        default=MAX_SHOW,
        help="Maximum size string field to collect.")
    parser.add_argument(
        '--procs',
        type=int,
        default=5,
        help="Number of processes to run.")
    parser.add_argument(
        '--select',
        help="Lambda expression for selecting rows.")
    args = parser.parse_args()

    fc = FieldChars.evaluate(args.file, **vars(args))
    print(fc.report(args.max_show, args.corr))
