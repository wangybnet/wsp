#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import logging

import yaml

import wsp
from wsp.fetcher.fetcher import Fetcher
from wsp.fetcher.config import FetcherConfig


if __name__ == "__main__":
    home_dir = sys.argv[1]
    fetcher_yaml = sys.argv[2]
    conf = {}
    try:
        with open(fetcher_yaml, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
    except Exception:
        print("Cannot load \"fetcher.yaml\".")
        exit(1)
    wsp.set_logger(getattr(logging, conf.get("log_level", "INFO").upper(), "INFO"),
                   format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
                   date_format="%b. %d,%Y %H:%M:%S",
                   log_file=conf.get("log_file"))
    log = logging.getLogger("wsp")
    log.debug("fetcher.yaml=%s" % conf)

    fetcher = Fetcher(FetcherConfig(home_dir, **conf))
    fetcher.start()
