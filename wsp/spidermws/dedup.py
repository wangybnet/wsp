# coding=utf-8

import logging

from pymongo import MongoClient

from wsp.utils.parse import extract_request
from wsp.errors import IgnoreRequest
from wsp.http import HttpRequest

log = logging.getLogger(__name__)


class MongoDedupMiddleware:
    """
    利用MongoDB去重
    """

    def __init__(self, mongo_addr, mongo_db, mongo_coll):
        self._mongo_addr = mongo_addr
        self._mongo_db = mongo_db
        self._mongo_coll = mongo_coll
        self._mongo_client = MongoClient(self._mongo_addr)

    @classmethod
    def from_config(cls, config):
        return cls(config.get("dedup_mongo_addr"),
                   config.get("dedup_mongo_db", "wsp"),
                   config.get("dedup_mongo_coll"))

    async def handle_input(self, response):
        request = response.request
        if self._is_dup(self._get_dedup_tbl_name(request), request, True):
            raise IgnoreRequest("The request (method=%s, url=%s) is duplicated" % (request.method, request.url))

    async def handle_output(self, response, result):
        return self._handle_output(response, result)

    def _handle_output(self, response, result):
        for r in result:
            if isinstance(r, HttpRequest):
                if not self._is_dup(self._get_dedup_tbl_name(response.request), r, False):
                    yield r
                else:
                    log.debug("The request (method=%s, url=%s) is duplicated" % (r.method, r.url))
            else:
                yield r

    def _is_dup(self, tbl_name, request, is_input):
        tbl = self._mongo_client[self._mongo_db][tbl_name]
        url = "%s %s" % (request.method, request.url)
        res = tbl.find_one({"url": url})
        if res is None:
            if is_input:
                tbl.insert_one({"url": url})
            return False
        return True

    def _get_dedup_tbl_name(self, request):
        req = extract_request(request)
        return self._mongo_coll or ("dedup_%s" % req.task_id)
