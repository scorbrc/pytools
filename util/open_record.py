"""
OpenRecord is a mutable ordered dictionary with methods for attributes.
"""
from collections import OrderedDict
from copy import deepcopy
import csv
import datetime as dt
from decimal import Decimal
import io
import json
import sys
import types
from typing import Callable
from .text_fmt import format_text_table


def is_num(x):
    """ Returns True if 'x' is a number: float, decimal, int. """
    try:
        float(x)
        return True
    except BaseException:
        return False


def to_safe_json(x):
    """ Convert 'x' to field type safe to output as JSON. """
    if isinstance(x, dict):
        return OrderedDict(
            [(key, to_safe_json(val)) for key, val in x.items()])
    elif isinstance(x, (list, tuple, set)) or 'ndarray' in str(type(x)):
        return [to_safe_json(elem) for elem in x]
    elif isinstance(x, dt.datetime):
        return x.isoformat()
    else:
        return x


def to_str(x, digits=3, max_len=120):
    """ Convert 'x' to a string, formatted according to its type. """
    if x is None:
        return ''
    if isinstance(x, str):
        return x[:max_len]
    if isinstance(x, int):
        return '%d' % x
    if isinstance(x, (Decimal, float)):
        return ('%%.%df' % digits) % x
    if isinstance(x, dt.datetime):
        return x.isoformat()
    if isinstance(x, (OpenRecord, dict, list, tuple, Callable)):
        return ''
    return str(x)


class OpenRecord(OrderedDict):
    """
    A mutable record based on an OrderedDictionary. Fields can be set and
    accessed as properties in addition to the dictionary style access.
    """

    def __init__(self, *args, **kwargs):
        """ Create an record with the same types of parameters
            accepted by OrderedDict. Any embedded dictionaries or lists
            of dictionaries will also be converted into OpenRecord's."""
        super(OpenRecord, self).__init__(*args, **kwargs)
        for key, val in self.items():
            if isinstance(val, dict):
                self[key] = OpenRecord(val)
            elif isinstance(val, (list, tuple)):
                for i in range(len(val)):
                    if isinstance(val[i], dict):
                        val[i] = OpenRecord(val[i])
        self.__key_fields = []
        self._initialized = True

    def add_key(self, *flds):
        """ Specify 'flds' as the key fields in the record. """
        self.__key_fields.extend(flds)

    def add_method(self, method, name):
        """ Add 'method' called 'name' to the record. """
        self[name] = types.MethodType(method, self)

    def __cmp(self, other):
        """ Compare 'self' to 'other' returning -1 if self is less than other,
            1 if self greater than other, 0 if equal. """
        rslt = 0
        if isinstance(other, OpenRecord):
            k0 = repr(self)
            k1 = repr(other)
            rslt = -1 if k0 < k1 else 1 if k0 > k1 else 0
        return rslt

    def __eq__(self, other): return self.__cmp(other) == 0
    def __ge__(self, other): return self.__cmp(other) >= 0
    def __gt__(self, other): return self.__cmp(other) > 0
    def __le__(self, other): return self.__cmp(other) <= 0
    def __lt__(self, other): return self.__cmp(other) < 0
    def __ne__(self, other): return self.__cmp(other) != 0

    def __getattr__(self, name):
        """ Retrieve attribute by name. """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __hash__(self):
        """ Produce a hash code for use in sets and dictionaries. """
        return hash(repr(self))

    def __repr__(self):
        """ Flattened representation of key fields if given or all fields. """
        def to_repr(x):
            if isinstance(x, dict):
                vals = ["%s=%s" % (k, to_repr(x[k])) for k in sorted(x)]
                return "{%s}" % ','.join(vals)
            elif isinstance(x, (list, tuple)):
                vals = [to_repr(v) for v in sorted(x)]
                return "[%s]" % ','.join(vals)
            else:
                return str(x)
        if len(self.__key_fields):
            obj = self.select(*self.__key_fields)
        else:
            obj = self
        return to_repr(obj)

    def __setattr__(self, name, value):
        """ Set attribute by name, creating it if non-existant. """
        if hasattr(self, '_initialized'):
            super(OpenRecord, self).__setitem__(name, value)
        else:
            super(OpenRecord, self).__setattr__(name, value)

    def __str__(self):
        """ Return string report of the record. """
        return self.to_pretty_json()

    def select(self, fields, exclude=False):
        """ Produce a new record with only 'fields' selected if 'exclude'
            is False or ony fields not in 'fields' if 'exclude' is True. """
        if not exclude:
            return OpenRecord(
                [(fn, self[fn]) for fn in fields if fn in self])
        else:
            return OpenRecord(
                [(k, v) for k, v in self.items() if k not in fields])

    def to_json(self):
        """ Generate unformatted JSON from the record. """
        return json.dumps(to_safe_json(self))

    def to_pretty_json(self):
        """ Generate formatted JSON from the record. """
        return json.dumps(to_safe_json(self), indent=4)

    @classmethod
    def create_from_csv(cls, src):
        """ Create records from CSV 'src', a file handler or string. """
        recs = []
        if hasattr(src, 'fileno'):
            src = src.read()
        else:
            with open(src) as fi:
                src = fi.read()
        sniffer = csv.Sniffer()
        reader = csv.reader(io.StringIO(src))
        names = []
        for row in reader:
            if not len(names):
                if sniffer.has_header(src):
                    names = row
                    # for x in row:
                    #    names.append(x.replace('\ufeff', ''))
                else:
                    names = ['fld_%02d' % (i + 1) for i in range(len(row))]
            else:
                recs.append(OpenRecord(zip(names, row)))
        return recs

    @classmethod
    def create_from_json(cls, src):
        """
        Create records from JSON 'src', which can be a file or string. The JSON
        can be a single object, list of objects or a separate JSON per line.
        """
        if hasattr(src, 'fileno'):
            src = src.read()
        try:
            # Try source as a complete JSON document.
            src_recs = json.loads(src)
            if isinstance(src_recs, (list, tuple)):
                return [OpenRecord(rec) for rec in src_recs]
            return OpenRecord(src_recs)
        except json.decoder.JSONDecodeError:
            # Try source as each line being a JSON document.
            for line in io.StringIO(src):
                src_recs = json.loads(line.strip())
                if isinstance(src_recs, (list, tuple)):
                    return [OpenRecord(rec) for rec in src_recs]
                return OpenRecord(src_recs)
        except TypeError:
            return [OpenRecord.create_from_json(x) for x in src]
        return None

    @classmethod
    def normalize(cls, records, default_value=None):
        """ Ensure that all 'records' have the same superset of fields. """
        names = []
        for rec in records:
            for n in rec:
                if n not in names:
                    names.append(n)
        nrecs = []
        for rec in records:
            nrec = deepcopy(rec)
            for n in sorted(names):
                if n not in nrec:
                    nrec[n] = default_value
            nrecs.append(nrec)
        return nrecs

    @classmethod
    def to_csv(cls, records, fo=sys.stdout):
        """ Generate CSV for 'records' writen to 'fo'. """
        if len(records) > 0:
            wrt = csv.writer(fo)
            wrt.writerow(records[0].keys())
            for rec in records:
                wrt.writerow([to_str(x) for x in rec.values()])

    @classmethod
    def to_text(cls, records, by_rows=False, by_cols=False, digits=3):
        return format_text_table(records, by_rows, by_cols, digits=digits);


    @classmethod
    def to_text_cols(cls, records, digits=3, max_len=80, indent=0):
        """
        Formats 'records' into text columns. Records are laid out
        in columns with the first column being the field name. 'digits'
        specifies precison for floating or decimal fields. 'max_len' is the
        maximum length printed for strings. 'indent' will indent the table the
        specified number of spaces.
        """
        records = [records] if isinstance(records, dict) else records
        cv_recs = []
        for rec in records:
            flds = [(fn, to_str(rec[fn], digits, max_len)) for fn in rec]
            cv_recs.append(OrderedDict(flds))
        so = io.StringIO()
        fn_len = max([len(fn) for fn in cv_recs[0]])
        col_lens = [max([len(x) for x in cr.values()]) for cr in cv_recs]
        for i, fn in enumerate(cv_recs[0]):
            row = [cr[fn].rjust(ln) for ln, cr in zip(col_lens, cv_recs)]
            print("%s%s %s" %
                  (' '.ljust(indent), fn.ljust(fn_len), ' '.join(row)),
                  file=so)
        return so.getvalue().rstrip()

    @classmethod
    def to_text_rows(cls, records, digits=3, max_len=80, indent=0):
        """
        Formats 'records' into evenly spaced text rows. 'digits'
        specifies precison for floating or decimal fields. 'max_len' is the
        maximum length printed for strings. 'indent' will indent the table the
        specified number of spaces.
        """
        records = [records] if isinstance(records, dict) else records

        # Convert fields to printable text.
        cv_recs = []
        for rec in records:
            flds = [(fn, to_str(rec[fn], digits, max_len)) for fn in rec]
            cv_recs.append(OrderedDict(flds))

        # find the max length of each convertedf field.
        fld_lens = OrderedDict()
        for cr in cv_recs:
            for fn, fv in cr.items():
                try:
                    fld_lens[fn] = max(fld_lens[fn], len(fv))
                except KeyError:
                    fld_lens[fn] = len(fv)

        # Filter fields with values, length > 0, add in field name max size.
        fld_lens = OrderedDict(
            [(fn, max(fl, len(fn))) for fn, fl in fld_lens.items() if fl > 0])

        # Build the report.
        so = io.StringIO()
        for i, cr in enumerate(cv_recs):
            so.write(' ' * indent)
            if i == 0:
                for j, fn in enumerate(fld_lens):
                    if j > 0:
                        so.write(' ')
                    so.write(fn.ljust(fld_lens[fn]))
                print(file=so)
            for j, fn in enumerate(fld_lens):
                if j > 0:
                    so.write(' ')
                if is_num(cr[fn]):
                    so.write(cr[fn].rjust(fld_lens[fn]))
                else:
                    so.write(cr[fn].ljust(fld_lens[fn]))
            print(file=so)
        return so.getvalue().rstrip()
