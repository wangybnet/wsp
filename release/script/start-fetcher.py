# coding=utf-8

import os
import logging

import yaml

import wsp
from wsp.fetcher.fetcher import Fetcher
from wsp.fetcher.config import FetcherConfig


if __name__ == "__main__":
    fetcher_yaml = "%s/fetcher.yaml" % os.getenv("WSP_CONF_DIR")
    conf = {}
    try:
        with open(fetcher_yaml, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
    except Exception:
        print("Cannot load '%s'" % fetcher_yaml)
        exit(1)
    else:
        conf.setdefault("fetcher_dir", "%s/data" % os.getenv("WSP_HOME"))
    wsp.set_logger(getattr(logging, os.getenv("WSP_LOG_LEVEL", "INFO").upper(), "INFO"),
                   format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
                   date_format="%d/%b/%Y %H:%M:%S")
    log = logging.getLogger("wsp")
    log.debug("fetcher.yaml=%s" % conf)

    fetcher = Fetcher(FetcherConfig(**conf))
    fetcher.start()
