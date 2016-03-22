#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import logging

import yaml

import wsp
from wsp.fetcher.Fetcher import Fetcher


if __name__ == "__main__":
    fetcher_yaml = sys.argv[1]
    conf = {}
    try:
        with open(fetcher_yaml, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
    except Exception:
        print("Cannot load \"fetcher.yaml\".")
        exit(1)
    wsp.set_logger(getattr(logging, conf.get("log_level", "WARNING").upper(), "WARNING"),
                   "%(asctime)s %(filename)s: [%(levelname)s] %(message)s",
                   "%b.%d,%Y %H:%M:%S")
    log = logging.getLogger("wsp")
    log.debug("fetcher.yaml=%s" % conf)
    fetcher = Fetcher(conf["master_addr"], conf["fetcher_addr"], int(conf["downloader_clients"]))
    fetcher.start()
