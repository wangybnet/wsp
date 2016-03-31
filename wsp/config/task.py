# coding=utf-8

START_URLS = "start_urls"
DOWNLOADER_MIDDLEWARES = "downloader_middlewares"
SPIDER_MIDDLEWARES = "spider_middlewares"
SPIDER = "spider"

DEFAULT_CONFIG = {START_URLS: [],
                  DOWNLOADER_MIDDLEWARES: [],
                  SPIDER_MIDDLEWARES: [],
                  SPIDER: None}


class TaskConfig:
    def __init__(self, **kw):
        self._config = dict(kw)

    def get(self, name, default=None):
        res = self._config.get(name, default)
        if res is None and name in DEFAULT_CONFIG:
            res = DEFAULT_CONFIG[res]
        return res

    def set(self, name, value):
        self._config[name] = value

    def set_default(self, name, value):
        self._config.setdefault(name, value)
