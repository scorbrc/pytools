""" Formats records (dictionaries) into text reports. """
from collections import OrderedDict
import datetime as dt
from decimal import Decimal
import io
from .util_tools import is_num, to_str


def to_text_cols(records, digits=3, max_len=80, indent=0, colnames=None):
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
        if i == 0:
            if colnames is not None:
                print("%s %s" %
                      (''.ljust(max_len),
                       ' '.join([cn.rjust(max_len) for cn in colnames])),
                      file=so)
        row = [cr[fn].rjust(ln) for ln, cr in zip(col_lens, cv_recs)]
        print("%s%s %s" %
              (' '.ljust(indent), fn.ljust(fn_len), ' '.join(row)),
              file=so)
    return so.getvalue().rstrip()


def to_text_rows(records, digits=3, max_len=80, indent=0):
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
