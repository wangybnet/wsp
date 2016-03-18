#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys

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
    fetcher = Fetcher(conf["master_addr"], conf["fetcher_addr"], conf["downloader_clients"])
    fetcher.start()
