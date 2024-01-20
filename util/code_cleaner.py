#!/usr/bin/env python3
"""
Run flake8 to find issues and autopep8 and autoflake to attempt to clean
up issues in sources in-place. Reports modules cleaned-up and modules that
could not be cleaned-up.
"""
from collections import namedtuple
from subprocess import run
import sys

Source = namedtuple('Source', ('file', 'line', 'char', 'err', 'msg'))


def run_flake8(files):
    """
    Run flake8 on 'files' source modules. Return dictionary for each
    source module issue found by source file path.
    """
    sources = {}
    for fp in files:
        cmd = "python3 -m flake8 --max-line-length=83 %s" % fp
        result = run(cmd, capture_output=True, shell=True)
        if len(result.stderr) > 0:
            raise RuntimeError(result.stderr.decode("utf-8").strip())
        for line in result.stdout.decode("utf-8").split('\n'):
            a, _, b = line.partition(' ')
            x = a.split(':')
            if len(x) >= 3:
                fp, ln, cn = x[:3]
                err, _, msg = b.partition(' ')
                src = Source(fp, int(ln), int(cn), err, msg)
                sources.setdefault(src.file, [])
                sources[src.file].append(src)
    return sources


def run_autopep8(sources):
    """
    Run autopep8 code cleaner and formatter on the sources modules in
    'source'. Writes cleaned and formatted source inplace.
    """
    for fp in sorted(sources):
        run("autopep8 -i -a %s" % fp, shell=True)


def run_autoflake(sources):
    """
    Run autoflake code cleaner on source modules in-place. This will remove
    unused imports and variables.
    """
    for fp in sorted(sources):
        cmd = ' '.join(('autoflake',
                        '--in-place',
                        '--remove-all-unused-imports',
                        '--remove-unused-variables',
                        fp))
        run(cmd, shell=True)


if __name__ in '__main__':

    files = sys.argv[1:]
    src1 = run_flake8(files)
    if len(src1) > 0:
        print("%d sources have issues; try cleaning up..." % len(src1))
        run_autopep8(src1)
        run_autoflake(src1)
        print("Look for remaining issues...")
        src2 = run_flake8(files)
        cleaned_sources = set()
        for fp in sorted(src1):
            for src in src1[fp]:
                if fp not in src2 or src not in src2[fp]:
                    cleaned_sources.add(src)
        if len(cleaned_sources):
            print("Cleaned up %d sources:" % len(cleaned_sources))
            for src in sorted(list(cleaned_sources)):
                print(src)
        if len(src2) > 0:
            print("\nUnable to clean:")
            for fp in sorted(src2):
                for src in src2[fp]:
                    print(src)
    else:
        print("Source files clean.")
