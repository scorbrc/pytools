""" Formats records (dictionaries) into text reports. """
from collections import OrderedDict
import datetime as dt
from decimal import Decimal
import io


def is_num(x):
    """ Return True if 'x' is a number. """
    try:
        float(x)
        return True
    except Exception:
        return False


def format_text_table(records,
                      by_rows=False,
                      by_cols=False,
                      colnames=None,
                      digits=3):
    """
    Formats one or more 'records' which are dictionaries of names and values,
    into evenly spaced text table. If 'by_rows' is True then records are laid
    out in rows. If 'by_col' is True then records are laid out in columns
    with the first column being the field names. Default is by rows if
    neither specified. """
    records = [records] if isinstance(records, dict) else records
    if not by_rows and not by_cols:
        by_rows = True
    cvrecs = []
    fields = OrderedDict()
    for rec in records:
        cvrec = OrderedDict()
        for fld in rec:
            fields.setdefault(fld, len(fld))
            if rec[fld] is not None:
                if isinstance(rec[fld], str):
                    cvrec[fld] = rec[fld]
                elif isinstance(rec[fld], int):
                    cvrec[fld] = '%d' % rec[fld]
                elif isinstance(rec[fld], (Decimal, float)):
                    cvrec[fld] = ('%%.%df' % digits) % rec[fld]
                elif isinstance(rec[fld], dt.datetime):
                    cvrec[fld] = rec[fld].strftime('%Y-%m-%dT%H:%M:%S')
                else:
                    cvrec[fld] = str(rec[fld])
            else:
                cvrec[fld] = ''
            fields[fld] = max(fields[fld], len(cvrec[fld]))
        cvrecs.append(cvrec)
    so = io.StringIO()
    if by_cols:
        max_len = max(fields.values())
        for i, fld in enumerate(fields):
            if i == 0:
                if colnames is not None and len(colnames) == len(records):
                    print("%s %s" %
                          (''.ljust(max_len),
                           ' '.join([cn.rjust(max_len) for cn in colnames])),
                          file=so)
            print("%s %s" %
                  (fld.ljust(max_len),
                   ' '.join([cvrec[fld].rjust(max_len) for cvrec in cvrecs])),
                  file=so)
    elif by_rows:
        for i, cvrec in enumerate(cvrecs):
            if i == 0:
                print(' '.join([fld.rjust(fields[fld])
                                if is_num(cvrec[fld])
                                else fld.ljust(fields[fld])
                                for fld in fields]), file=so)

            print(' '.join([cvrec[fld].rjust(fields[fld])
                            if is_num(cvrec[fld])
                            else cvrec[fld].ljust(fields[fld])
                            for fld in fields]), file=so)
    return so.getvalue().strip()
