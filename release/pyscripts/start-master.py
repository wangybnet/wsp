#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from wsp.master.master import Master
import yaml
import sys


if __name__ == "__main__":

    def get_master_yaml(master_yaml):
        try:
            with open(master_yaml, "r", encoding="utf-8") as f:
                dict = yaml.load(f)
                return dict
        except Exception:
            print("Loafing master.yaml is failed")

    conf = get_master_yaml(sys.argv[1])
    master = Master(config)
    master.start()
