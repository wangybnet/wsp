# coding=utf-8

import sys
import logging

# Add patch to avoid 'TIME_WAIT'
from . import _patch
del _patch

# Check minimum required Python version
assert sys.version_info >= (3, 5), "Python 3.5+ is required."


# Set logger
def set_logger(level, format=None, date_format=None):
    log = logging.getLogger(__name__)
    log.setLevel(level)
    log_handler = logging.StreamHandler()
    formatter = logging.Formatter(format, date_format)
    log_handler.setFormatter(formatter)
    log.addHandler(log_handler)
    log.hasHandlers()
