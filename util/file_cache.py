"""
A file cache for JSON objects.
"""
import hashlib
import json
import os
from time import time


class FileCache:
    """ File cache for JSON objects. """

    PARTITIONS = 100

    def __init__(self, base_dir='cache', expire_secs=60 * 60 * 24 * 7):
        """
        Create FileCache using 'base_dir' as the root for cache directories
        and 'expire_secs' as the number of seconds to keep a cached file.
        """
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        self.__base_dir = base_dir
        self.__expire_secs = expire_secs

    def add(self, name, content):
        """
        Add 'content', which must be JSON serializable, to the file cache
        stored under 'name'.
        """
        fp = self.__path(name)
        with open(fp, 'w') as fo:
            json.dump(content, fo)

    def clean(self, expire_secs=None):
        """ Clean cache of expired files older than 'expire_secs'. """
        if expire_secs is None:
            expire_secs = self.__expire_secs
        deletes = []
        for root, dirs, files in os.walk(self.__base_dir):
            for name in files:
                fp = os.path.join(root, name)
                if time() - os.path.getmtime(fp) > expire_secs:
                    deletes.append(fp)
        for fp in deletes:
            os.remove(fp)
        return len(deletes)

    def get(self, name):
        """ Get content from cache stored under 'named'. """
        fp = self.__path(name)
        if os.path.exists(fp) and os.path.getsize(fp) > 0:
            if time() - os.path.getmtime(fp) < self.__expire_secs:
                with open(fp) as fi:
                    return json.loads(fi.read())
        return None

    def __path(self, name):
        """ Convert 'name' into a path. """
        key = str(hashlib.sha224(name.encode('UTF-8')).hexdigest())
        pn = hash(key) % FileCache.PARTITIONS
        fd = os.path.join(self.__base_dir, "%02d" % pn)
        if not os.path.exists(fd):
            os.mkdir(fd)
        return "%s/%s.json" % (fd, key)


if __name__ == '__main__':

    from random import choices
    import string
    from time import sleep

    def random_b36(n_chars):
        return ''.join(
            choices(string.digits + string.ascii_uppercase, k=n_chars))

    count = 10000
    base_dir = 'test_cache'

    fc = FileCache(base_dir)
    n = fc.clean(0)

    st = time()
    keys = {}
    for _ in range(count):
        key = random_b36(32)
        rec = {k: random_b36(100) for k in string.ascii_lowercase}
        fc.add(key, rec)
        keys[key] = rec
        sleep(.0025)

    for key in keys:
        rec = fc.get(key)
        if rec is None:
            print("%s not found" % key)
        elif rec != keys[key]:
            print("%s content changed: %s != %s" % (key, recv, keys[key]))

    clean_n = fc.clean()
    print("Cleaned %d files." % clean_n)

    fc = FileCache(base_dir, expire_secs=(time() - st) / 2)
    clean_n = fc.clean()
    print("Cleaned %d files." % clean_n)

    fc = FileCache(base_dir)
    found_n = 0
    for key in keys:
        rec = fc.get(key)
        if rec is not None:
            found_n += 1

    if found_n + clean_n != count:
        print("File counts wrong after cleaning: %d+%d != %d." %
              (found_n, clean_n, count))
