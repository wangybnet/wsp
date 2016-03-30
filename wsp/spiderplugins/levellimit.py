# coding=utf-8

import logging

from wsp import reqmeta
from wsp.downloader.http import HttpRequest
from wsp.config import task as tc

log = logging.getLogger(__name__)


class LevelLimitPlugin:
    """
    限制爬取深度

    初始页面层数为0。
    """

    def __init__(self, max_level):
        self._max_level = max_level

    @classmethod
    def from_config(cls, config):
        return cls(config.get(tc.MAX_LEVEL))

    async def handle_response(self, request, response, result):
        return self._handle_response(request, result)

    def _handle_response(self, request, result):
        level = request.meta.get(reqmeta.CRAWL_LEVEL, 0) + 1
        for r in result:
            if isinstance(r, HttpRequest):
                if level > self._max_level:
                    yield None
                else:
                    r.meta[reqmeta.CRAWL_LEVEL] = level
                    yield r
            else:
                yield r
