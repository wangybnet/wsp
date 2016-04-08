# coding=utf-8

import os
import sys
import logging

# Add patch to avoid 'TIME_WAIT'
from . import _patch
del _patch

# Check minimum required Python version
assert sys.version_info >= (3, 5), "Python 3.5+ is required."


# Set logger
def set_logger(level, format=None, date_format=None, *, log_file=None):
    log = logging.getLogger(__name__)
    log.setLevel(level)
    console = logging.StreamHandler()
    formatter = logging.Formatter(format, date_format)
    console.setFormatter(formatter)
    log.addHandler(console)
    if log_file:
        try:
            i = log_file.rindex("/")
            log_dir = log_file[:i]
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, mode=0o775)
        except ValueError:
            pass
        file = logging.FileHandler(log_file)
        file.setFormatter(formatter)
        log.addHandler(file)
