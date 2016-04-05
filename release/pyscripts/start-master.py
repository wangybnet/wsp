#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import logging

import yaml

import wsp
from wsp.master.master import Master
from wsp.master.config import MasterConfig
from wsp.config.system import SystemConfig


if __name__ == "__main__":

    def get_yaml(yaml_file):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                dict = yaml.load(f)
                return dict
        except Exception:
            print("Loafing '%s' is failed" % yaml_file)
            exit(1)

    master_conf = get_yaml(sys.argv[1])
    system_conf = get_yaml(sys.argv[2])
    wsp.set_logger(getattr(logging, master_conf.get("log_level", "INFO").upper(), "INFO"),
                   format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
                   date_format="%b.%d,%Y %H:%M:%S",
                   log_file=master_conf.get("log_file"))
    log = logging.getLogger("wsp")
    log.debug("master.yaml=%s" % master_conf)
    log.debug("system.yaml=%s" % system_conf)

    master = Master(MasterConfig(**master_conf), SystemConfig(**system_conf))
    master.start()
