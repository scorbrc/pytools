""" Utility tools. """
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from difflib import SequenceMatcher
from numbers import Number
import operator
import os
import sys
from typing import Callable


def find_lcs(names):
    """ Finds longest common substring among the strings in 'names'. """
    sub_counts = defaultdict(int)
    for i in range(0, len(names)):
        for j in range(i + 1, len(names)):
            sm = SequenceMatcher(None, names[i], names[j])
            match = sm.find_longest_match(0, len(names[i]), 0, len(names[j]))
            match_sub = names[i][match.a:match.a + match.size]
            sub_counts[match_sub] += 1
    common_sub = max(sub_counts.items(), key=operator.itemgetter(1))[0]
    return common_sub, [name.replace(common_sub, '') for name in names]


def flatten_list(x):
    """ Flatten sub-lists embedded in 'ls'. """
    def _flatten_list_(x, fls):
        if isinstance(x, (list, tuple)):
            for y in x:
                if isinstance(y, (list, tuple)):
                    for z in y:
                        _flatten_list_(z, fls)
                else:
                    fls.append(y)
        else:
            fls.append(x)
        return fls
    return _flatten_list_(x, [])


def get_default(args, name, def_val=None):
    """ Get 'name' from args if it is contained in 'args' and not None,
    otherwise return default value 'def_val'. """
    if not is_empty(args, name):
        return args[name]
    return def_val


def get_env_prompt(env_name):
    """ Attempt to fetch 'env_name' from environment variables,
    prompt for value if it does not exist. """
    if env_name in os.environ:
        return os.environ[env_name]
    return input("%s:" % env_name)


def is_empty(value, key=None):
    """ Returns true if 'value' or 'value[key]' has no value(s). """
    test_val = None
    if key is not None and isinstance(value, dict):
        try:
            test_val = value[key]
        except KeyError:
            pass
    else:
        test_val = value

    if test_val is None:
        return True

    if isinstance(test_val, Number):
        return False

    if isinstance(test_val, str):
        if len(test_val.strip()) == 0 or test_val == 'null':
            return True
    else:
        try:
            iter(test_val)
            if len(test_val) == 0:
                return True
        except TypeError:
            pass

    return False


def is_list(x):
    """ Returns true if 'x' is a list. """
    return isinstance(x, (list, tuple))


def is_num(x):
    """ Return True if 'x' is a number. """
    try:
        float(x)
        return True
    except Exception:
        return False


def import_name(module, name):
    """
    Dynamically loads 'name' method, class, and the like from 'module',
    which must be relative to the. current path or on PYTHONPATH
    """
    try:
        mod = __import__(module, globals(), locals(), [name])
        try:
            return getattr(mod, name)
        except AttributeError as ex:
            raise AttributeError(
                "%s does not contain %s: %s" %
                (module, name, ex))
    except ImportError as ex:
        raise ImportError("Failed to import module %s: %s" % (module, ex))


def to_camel_name(name):
    """ Converts names like get_http_response_code to getHttpResponseCode."""
    result = []
    i = 0
    while i < len(name):
        if name[i] == '_' and i > 0 and i < len(name) - 1:
            result.append(name[i + 1].upper())
            i += 1
        else:
            result.append(name[i])
        i += 1
    return ''.join(result)


def to_snake_name(name):
    """ Converts names like getHttpResponseCode to get_http_response_code. """
    result = []
    chx = [c if c.isalnum() else '_' for c in name.strip()]
    for i, ch in enumerate(chx):
        if ch.isupper():
            if ((i - 1 > 0 and chx[i - 1].islower()) or
                    (i - 1 > 0 and i + 1 < len(chx) and chx[i + 1].islower())):
                result.append("_%s" % ch.lower())
            else:
                result.append(ch.lower())
        else:
            result.append(ch)
    sn_name = ''.join(result)
    while '__' in sn_name:
        sn_name = sn_name.replace('__', '_')
    return sn_name


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
    if isinstance(x, datetime):
        return x.isoformat()
    if isinstance(x, (dict, list, tuple, Callable)):
        return ''
    return str(x)


class NameTransformer():
    """
    Transforms names with any function that accepts a strings and produces
    a transformed string. Caches the transformation for repeating strings.
    """

    def __init__(self, trans_fn=to_snake_name):
        """ Create a name transformer using 'trans_fn'. """
        self.__trans_fn = trans_fn
        self.__transformed = {}
        self.__count = 0

    def __len__(self):
        return len(self.__transformed)

    def transform(self, name):
        """ Transform 'name'. """
        self.__count += 1
        try:
            return self.__transformed[name]
        except KeyError:
            xn = self.__trans_fn(name)
            self.__transformed[name] = xn
            return xn


def zero_if_none(x):
    """ Returns zero(s) for None values. If 'x' is sequence then
    sequence with Nones replaced by zeros is returned. """
    if is_list(x):
        return [v if v is not None else 0 for v in x]
    else:
        return x if x is not None else 0
