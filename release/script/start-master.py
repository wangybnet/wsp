# coding=utf-8

import os
import sys
import logging

wsp_lib = "%s/lib" % os.getenv("WSP_HOME")
if wsp_lib not in sys.path:
    sys.path.append(wsp_lib)

import yaml

import wsp
from wsp.master import Master
from wsp.config import MasterConfig, SystemConfig


if __name__ == "__main__":

    def get_yaml(yaml_file):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                dict = yaml.load(f)
                return dict
        except Exception:
            print("Cannot load '%s'" % yaml_file)
            exit(1)

    conf_dir = os.getenv("WSP_CONF_DIR")
    master_conf = get_yaml("%s/master.yaml" % conf_dir)
    system_conf = get_yaml("%s/system.yaml" % conf_dir)
    wsp.set_logger(getattr(logging, os.getenv("WSP_LOG_LEVEL", "INFO").upper(), "INFO"),
                   format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
                   date_format="%d/%b/%Y %H:%M:%S")
    log = logging.getLogger("wsp")
    log.debug("master.yaml=%s" % master_conf)
    log.debug("system.yaml=%s" % system_conf)

    master = Master(MasterConfig(**master_conf), SystemConfig(**system_conf))
    master.start()
