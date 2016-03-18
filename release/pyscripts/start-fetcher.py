#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import logging

import yaml

from wsp.fetcher.Fetcher import Fetcher


if __name__ == "__main__":
    print(sys.argv)
    fetcher_yaml = sys.argv[1]
    conf = {}
    try:
        with open(fetcher_yaml, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
            print(conf)
    except Exception:
        print("Cannot load \"fetcher.yaml\".")
        exit(1)
    logging.basicConfig(level=getattr(logging, conf.get("log_level", "WARNING").upper(), "WARNING"),
                        format='%(asctime)s %(filename)s: [%(levelname)s] %(message)s',
                        datefmt='%b.%d,%Y %H:%M:%S')
    logging.debug("master.yaml=%s" % conf)
    fetcher = Fetcher(conf["master_addr"], conf["fetcher_addr"], int(conf["downloader_clients"]))
    fetcher.start()
