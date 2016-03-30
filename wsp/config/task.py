# coding=utf-8

START_URLS = "start_urls"
MAX_RETRY_TIMES = "max_retry_times"
MAX_LEVEL = "max_level"
CHECK = "check"
FOLLOW = "follow"
DOWNLOADER_PLUGINS = "downloader_plugins"
SPIDER_PLUGINS = "spider_plugins"
SPIDER = "spider"
MONGO_ADDR = "mongo_addr"
AGENT_ADDR = "agent_addr"

DEFAULT_CONFIG = {START_URLS: [],
                  MAX_RETRY_TIMES: 3,
                  MAX_LEVEL: 0,
                  CHECK: [],
                  FOLLOW: {},
                  DOWNLOADER_PLUGINS: [],
                  SPIDER_PLUGINS: [],
                  SPIDER: None,
                  MONGO_ADDR: None,
                  AGENT_ADDR: None}


class TaskConfig:
    def __init__(self, **kw):
        self._config = dict(kw)

    def get(self, name):
        res = self._config.get(name)
        if not res:
            res = DEFAULT_CONFIG.get(name)
        return res

    def set(self, name, value):
        self._config[name] = value
