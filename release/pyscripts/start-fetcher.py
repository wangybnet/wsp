# coding=utf-8

import sys
import logging

import yaml


from wsp.fetcher.Fetcher import Fetcher


if __name__ == "__main__":
    print(sys.argv)
    fetcher_yaml = sys.argv[1]
    try:
        with open(fetcher_yaml, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
            print(conf)
    except Exception:
        print("Cannot load \"fetcher.yaml\".")
        exit(1)
    fetcher = Fetcher(conf["master"]["rpc_addr"], conf["fetcher"]["rpc_host"], conf["downloader"]["clients"])
    # TODO
