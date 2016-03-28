# coding=utf-8

import logging

from wsp import reqmeta
from wsp.downloader.http import HttpRequest

log = logging.getLogger(__name__)


class LevelLimitPlugin:
    """
    限制爬取深度

    初始页面层数为0。
    """

    def __init__(self, max_level):
        self._max_level = max_level

    async def handle_response(self, request, response, result):
        return self._handle_response(request, result)

    def _handle_response(self, request, result):
        level = request.meta.get(reqmeta.CRAWL_LEVEL) + 1
        if level <= self._max_level:
            return result
        return ((None if isinstance(r, HttpRequest) else r) for r in result)
