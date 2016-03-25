# coding=utf-8

import sys
import logging

# Check minimum required Python version
assert sys.version_info >= (3, 5), "Python 3.5+ is required."


# Set logger
def set_logger(level, fmt=None, datefmt=None):
    log = logging.getLogger(__name__)
    log.setLevel(level)
    console = logging.StreamHandler()
    formatter = logging.Formatter(fmt, datefmt)
    console.setFormatter(formatter)
    log.addHandler(console)
