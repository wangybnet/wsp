# coding=utf-8

import sys
import logging

# Check minimum required Python version
assert sys.version_info >= (3, 5), "Python 3.5+ is required."


# Set logger
def set_logger(level, format=None, datefmt=None):
    log = logging.getLogger(__name__)
    log.setLevel(level)
    console = logging.StreamHandler()
    formatter = logging.Formatter(format, datefmt)
    console.setFormatter(formatter)
    log.addHandler(console)
