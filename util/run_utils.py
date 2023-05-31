"""
Run time functions.
"""
import fcntl
import os
from subprocess import Popen, PIPE
import sys
import tempfile


def run_as_singleton(name=None):
    """
    Ensures a single instance of the calling script is running. Script 'name'
    is taken from sys.argv[0] by default and used to create a lock file in
    the temp directory. Returns True if lock is granted and False if not.
    Cleans up automatically when the single process finishes.
    """
    name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    fp = '{}/.{}.lock'.format(tempfile.gettempdir(), name)
    orig_umask = os.umask(0)
    try:
        lf_fd = os.open(fp, os.O_WRONLY | os.O_CREAT, 0o600)
        try:
            fcntl.lockf(lf_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            return False
    finally:
        os.umask(orig_umask)


def run_subproc(cmd, in_data=None):
    """
    Runs 'cmd' as a subprocess in a shell. 'in_data' passed as standard input
    if given. Standard output and error returned upon completed. RuntimeError
    thrown if 'cmd' fails to run of returns exit status 0.
    """
    if in_data is not None:
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
        out, err = proc.communicate(in_data.encode('UTF-8'))
    else:
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError("%s failed (%d) %s" % (cmd, proc.returncode, err))
    return out.decode('utf-8').strip()
