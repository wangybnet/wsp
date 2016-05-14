# coding=utf-8

import os
import sys
import logging

wsp_home = os.getenv("WSP_HOME")
if not wsp_home:
    wsp_home = "../"
wsp_conf_dir = os.getenv("WSP_CONF_DIR")
if not wsp_conf_dir:
    wsp_conf_dir = "%s/conf" % wsp_home
wsp_lib_dir = os.getenv("WSP_LIB_DIR")
if not wsp_lib_dir:
    wsp_lib_dir = "%s/lib" % wsp_home
if os.path.exists(wsp_conf_dir) and (wsp_lib_dir not in sys.path):
    sys.path.append(wsp_lib_dir)

import yaml

import wsp
from wsp.fetcher import Fetcher
from wsp.config import FetcherConfig


if __name__ == "__main__":
    fetcher_yaml = "%s/fetcher.yaml" % wsp_conf_dir
    conf = {}
    try:
        with open(fetcher_yaml, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
    except Exception:
        print("Cannot load '%s'" % fetcher_yaml)
        exit(1)
    else:
        conf.setdefault("fetcher_dir", "%s/data" % wsp_home)
    wsp.set_logger(getattr(logging, os.getenv("WSP_LOG_LEVEL", "INFO").upper(), "INFO"),
                   format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
                   date_format="%d/%b/%Y %H:%M:%S")
    log = logging.getLogger("wsp")
    log.debug("fetcher.yaml=%s" % conf)

    fetcher = Fetcher(FetcherConfig(**conf))
    fetcher.start()
