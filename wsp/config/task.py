# coding=utf-8

TASK_ID = "task_id"
START_URLS = "start_urls"
DOWNLOADER_MIDDLEWARES = "downloader_middlewares"
SPIDER_MIDDLEWARES = "spider_middlewares"
SPIDERS = "spiders"


class TaskConfig:
    def __init__(self, **kw):
        self._config = dict(kw)

    def get(self, name, default=None):
        return self._config.get(name, default)

    def setdefault(self, name, value):
        self._config.setdefault(name, value)

    def __getitem__(self, item):
        return self._config.get(item)

    def __setitem__(self, key, value):
        self._config[key] = value
