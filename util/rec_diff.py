"""
Compares two records that can be hierarchical arranged values, lists and
dictionaries. Reports differences in presence/absense, data types and values.
"""
from collections import namedtuple


"""
Records differences with field name 'key' type of difference (added, removed,
changed and type) 'diff', description 'desc' old type or value 'old', and
new type of value 'new'.
"""
RecDiff = namedtuple('RecDiff', ('key', 'diff', 'desc', 'old', 'new'))


def add_diff(key, diff, desc, old, new, diffs):
    if diff == 'type':
        old = type(old).__name__
        new = type(new).__name__
    diffs.append(RecDiff(key, diff, desc, old, new))


def is_excluded(key, excls):
    for exc in excls:
        if exc in key:
            return True
    return False


def rec_diff(key, old_rec, new_rec, excls=None, diffs=None):
    """
    Recursive record comparison between dictionary like objects
    'old_rec' and 'new_rec', which can have values, embedded lists or
    dictionaries. 'key' is the key for the next level in the two records
    as it recurses through the records. 'excls' is a set of key names
    to exclude from the comparison. Returns zero or more differences,
    where each difference has case, key (field name), difference description,
    old object asnd new object.
    """
    excls = [] if excls is None else excls
    diffs = [] if diffs is None else diffs
    if not is_excluded(key, excls):
        if isinstance(old_rec, (list, tuple)):
            # old_rec value is a list
            if not isinstance(new_rec, (list, tuple)):
                desc = 'new is not a list'
                add_diff(key, 'type', desc, old_rec, new_rec, diffs)
            else:
                btypes = set([type(x) for x in old_rec])
                ttypes = set([type(x) for x in new_rec])
                if len(btypes) == 1 and btypes == ttypes and list(
                        btypes)[0] == str:
                    # String array - compare using sets.
                    base_set = set(old_rec)
                    test_set = set(new_rec)
                    for d in base_set.difference(test_set):
                        desc = 'old not in new list'
                        add_diff(key, 'removed', desc, d, None, diffs)
                    for d in test_set.difference(base_set):
                        desc = 'new not in old list'
                        add_diff(key, 'added', desc, None, d, diffs)
                else:
                    # Array of objects - order by string representations and
                    # compare one by one.
                    bx = sorted([x for x in old_rec], key=lambda x: str(x))
                    tx = sorted([x for x in new_rec], key=lambda x: str(x))
                    diff_ct = len(diffs)
                    for i in range(max(len(bx), len(tx))):
                        if i < len(bx) and i < len(tx):
                            rec_diff(key, bx[i], tx[i], excls, diffs)
                        elif i < len(bx):
                            desc = 'old not in new object'
                            add_diff(
                                key, 'removed', desc, bx[i], None, diffs)
                        else:
                            desc = 'new not in old object'
                            add_diff(key, 'added', desc, None, tx[i], diffs)
                        if len(diffs) > diff_ct:
                            break
        elif isinstance(old_rec, dict):
            # old_rec value is an object
            if not isinstance(new_rec, dict):
                desc = 'new not a dict'
                add_diff(key, 'type', desc, old_rec, new_rec, diffs)
            for base_key in sorted(old_rec):
                bv = old_rec[base_key]
                if not is_excluded(base_key, excls):
                    full_key = "%s.%s" % (key, base_key)
                    if base_key not in new_rec:
                        desc = 'old key not in new dict'
                        add_diff(full_key, 'removed', desc, bv, None, diffs)
                    elif isinstance(bv, (list, tuple)):
                        tv = new_rec[base_key]
                        rec_diff(full_key, bv, tv, excls, diffs)
                    elif isinstance(old_rec[base_key], dict):
                        tv = new_rec[base_key]
                        rec_diff(full_key, bv, tv, excls, diffs)
                    else:
                        tv = new_rec[base_key]
                        if bv != tv:
                            desc = 'new dict value changed'
                            add_diff(
                                full_key, 'changed', desc, bv, tv, diffs)
            for test_key in sorted(new_rec, key=lambda k: str(k)):
                if not is_excluded(test_key, excls):
                    tv = new_rec[test_key]
                    full_key = "%s.%s" % (key, test_key)
                    if test_key not in old_rec:
                        desc = 'new key not in old dict'
                        add_diff(full_key, 'added', desc, None, tv, diffs)
        else:
            # base rec is a value
            if not isinstance(old_rec, type(new_rec)):
                desc = 'new not same type'
                add_diff(key, 'type', desc, old_rec, new_rec, diffs)
            elif old_rec != new_rec:
                desc = 'new value changed'
                add_diff(key, 'changed', desc, old_rec, new_rec, diffs)
    return diffs
