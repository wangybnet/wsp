# coding=utf-8

import logging

from wsp.http import HttpRequest

log = logging.getLogger(__name__)


class LimitLevelMiddleware:
    """
    限制爬取深度

    初始页面层数为0。
    """

    def __init__(self, max_level):
        self._max_level = max_level

    @classmethod
    def from_config(cls, config):
        return cls(config.get("max_level", 0))

    async def handle_output(self, response, result):
        return self._handle_output(response, result)

    def _handle_output(self, response, result):
        level = response.meta.get("crawl_level", 0) + 1
        for r in result:
            if isinstance(r, HttpRequest):
                if level <= self._max_level:
                    r.meta["crawl_level"] = level
                    yield r
                else:
                    log.debug("The request(url=%s) will be aborted as the level of it is out of limit" % r.url)
            else:
                yield r
