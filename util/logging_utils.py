import logging
from logging.handlers import RotatingFileHandler
import multiprocessing as mp
import os
from threading import get_native_id
import sys


def create_file_handler(fp, level=logging.INFO, max_bytes=2**24, backups=3):
    """
    Create file handler with file parth 'fp', logging 'level', maximum size
    of 'max_bytes' per file rotated between 'backups' number of files.
    """
    for x in fp.split('/'):
        if len(x) and os.path.isdir(x):
            if not os.path.exists(x):
                try:
                    os.mkdir(x)
                except FileExistsError:
                    pass
    hd = RotatingFileHandler(fp, maxBytes=max_bytes, backupCount=backups)
    hd.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - p%(process)d - t%(thread_id)d " +
            "%(filename)s:%(lineno)d - %(message)s"))
    hd.setLevel(level)
    hd.addFilter(get_logger_thread_id_filter)
    return hd


def create_stream_handler(level=logging.WARNING):
    """ Create a console logger with logging 'level'. """
    hd = logging.StreamHandler()
    hd.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    hd.setLevel(level)
    return hd

def get_default_app_name(app_name=None):
    """
    Creates a default application name if 'app_name' not given,
    based on the executing script name.
    """
    if app_name is None:
        return os.path.basename(os.path.splitext(sys.argv[0])[0])
    return app_name


def get_logger_info(logger=None):
    """
    Generates JSON description of 'logger' or all currently configured
    loggers if 'logger' not given.
    """
    info = {'root': {'logger': str(logging.getLogger()), 'handlers': []}}
    for h in logging.getLogger().handlers:
        info['root']['handlers'].append({str(h): h.formatter._fmt})
    for nm, lgr in logging.Logger.manager.loggerDict.items():
        if logger is None or logger == lgr:
            info[nm] = {'logger': str(lgr), 'handlers': []}
            if not isinstance(lgr, logging.PlaceHolder):
                for h in lgr.handlers:
                    info[nm]['handlers'].append({str(h): h.formatter._fmt})
    return info


def get_logger_thread_id_filter(record):
    """ Added thread id to logging 'record'. """
    record.thread_id = get_native_id()
    return record


def get_logger(app_name=None,
               console_level=logging.WARN,
               file_level=logging.INFO,
               file_dir='log',
               max_bytes=2**24,
               backups=3):
    """
    Get logger 'name', creating it first time.
    'console_level' sets logging level for stdout. None to suppress.
    'file_level' sets logging level for fiels. None to suppress.
    'file_dir' is directory to write log fiels to.
    'log_max_bytes' is the max size in bytes for each rotated log file.
    'log_backups' is the numebr of rotated log files.
    """
    app_name = get_default_app_name(app_name)
    pnum = [ch for ch in mp.current_process().name if ch.isdigit()]
    if len(pnum):
        app_name += '_' + ''.join(pnum)
    log = logging.getLogger(app_name)
    if not log.hasHandlers():
        log.setLevel(min(console_level, file_level))
        hd = create_file_handler(
            os.path.join(file_dir, app_name + '.log'),
            file_level,
            max_bytes,
            backups)
        log.addHandler(hd)
        if console_level is not None:
            hd = create_stream_handler(console_level)
            log.addHandler(hd)
    return log


def remove_handlers(logger_name='root'):
    logger = logging.getLogger(logger_name)
    while logger.hasHandlers():
        for h in list(logger.handlers):
            h.close()
            logger.removeHandler(h)


def setup_root_logger(app_name=None, file_dir='log', level=logging.INFO):
    """ Configures the root logger. """
    app_name = get_default_app_name(app_name)
    logging.getLogger().setLevel(level)
    hd = create_file_handler(os.path.join(file_dir, app_name + '.log'), level)
    logging.getLogger().addHandler(hd)
    hd = create_stream_handler(logging.WARNING)
    logging.getLogger().addHandler(hd)
    logging.info("-- %s %s", app_name, ' ' * (76 - len(app_name)))
