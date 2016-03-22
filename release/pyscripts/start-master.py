#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import logging

import yaml

import wsp
from wsp.master.master import Master
from wsp.master.config import WspConfig


if __name__ == "__main__":

    def get_master_yaml(master_yaml):
        try:
            with open(master_yaml, "r", encoding="utf-8") as f:
                dict = yaml.load(f)
                return dict
        except Exception:
            print("Loafing master.yaml is failed")
            exit(1)

    conf = get_master_yaml(sys.argv[1])
    wsp.set_logger(getattr(logging, conf.get("log_level", "WARNING").upper(), "WARNING"),
                   "%(asctime)s %(name)s: [%(levelname)s] %(message)s",
                   "%b.%d,%Y %H:%M:%S")
    log = logging.getLogger("wsp")
    log.debug("master.yaml=%s" % conf)

    master = Master(conf["master_addr"],
                    WspConfig(kafka_addr=conf["kafka_addr"],
                              mongo_addr=conf["mongo_addr"],
                              agent_addr=conf["agent_addr"]))
    master.start()
