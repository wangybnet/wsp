# coding=utf-8

import logging

from pymongo import MongoClient

from wsp.http import HttpRequest
from wsp.config import task as tc

log = logging.getLogger(__name__)


class MongoDedupMiddleware:
    """
    利用MongoDB去重
    """

    def __init__(self, mongo_addr, mongo_db, mongo_tbl):
        self._mongo_client = MongoClient(mongo_addr)
        self._dedup_tbl = self._mongo_client[mongo_db][mongo_tbl]
        self._dedup_tbl.create_index("url")

    @classmethod
    def from_config(cls, config):
        task_id = config.get(tc.TASK_ID)
        return cls(config.get("dedup_mongo_addr"),
                   config.get("dedup_mongo_db", "wsp"),
                   config.get("dedup_mongo_tbl", "dedup_%s" % task_id))

    async def handle_output(self, response, result):
        return self._handle_result(result)

    async def handle_start_requests(self, result):
        return self._handle_result(result)

    def _handle_result(self, result):
        for r in result:
            if isinstance(r, HttpRequest):
                if not self._is_dup(r):
                    yield r
                else:
                    log.debug("Find the request (method=%s, url=%s) is duplicated" % (r.method, r.url))
            else:
                yield r

    def _is_dup(self, request):
        url = "%s %s" % (request.method, request.url)
        res = self._dedup_tbl.find_one({"url": url})
        if res is None:
            self._dedup_tbl.insert_one({"url": url})
            return False
        return True
