#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys

import yaml

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

    conf = get_master_yaml(sys.argv[1])
    master = Master(conf["master_addr"],
                    WspConfig(kafka_addr=conf["kafka_addr"],
                              mongo_addr=conf["mongo_addr"],
                              agent_addr=conf["agent_addr"]))
    master.start()
