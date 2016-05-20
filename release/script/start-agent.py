# coding=utf-8

import os
import sys
import logging

wsp_home = os.getenv("WSP_HOME")
if not wsp_home:
    wsp_home = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
from wsp.agent import Agent
from wsp.config import AgentConfig


if __name__ == "__main__":
    agent_yaml = "%s/agent.yaml" % wsp_conf_dir
    conf = {}
    try:
        with open(agent_yaml, "r", encoding="utf-8") as f:
            conf = yaml.load(f)
    except Exception:
        print("Cannot load '%s'" % agent_yaml)
        exit(1)
    else:
        conf.setdefault("agent_dir", "%s/data" % wsp_home)
    wsp.set_logger(getattr(logging, os.getenv("WSP_LOG_LEVEL", "DEBUG").upper(), "INFO"),
                   format="%(asctime)s %(name)s: [%(levelname)s] %(message)s",
                   date_format="%d/%b/%Y %H:%M:%S")
    log = logging.getLogger("wsp")
    log.debug("agent.yaml=%s" % conf)

    agent = Agent(AgentConfig(**conf))
    agent.start()
