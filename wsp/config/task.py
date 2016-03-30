# coding=utf-8

START_URLS = "start_urls"
DOWNLOADER_PLUGINS = "downloader_plugins"
SPIDER_PLUGINS = "spider_plugins"
SPIDER = "spider"

DEFAULT_CONFIG = {START_URLS: [],
                  DOWNLOADER_PLUGINS: [],
                  SPIDER_PLUGINS: [],
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
