# coding=utf-8

import logging

from pymongo import MongoClient

from wsp.utils.fetcher import extract_request
from wsp.errors import IgnoreRequest

log = logging.getLogger(__name__)


class MongoDedupPlugin:
    """
    利用MongoDB去重
    """

    def __init__(self, mongo_addr, mongo_db):
        self._mongo_addr = mongo_addr
        self._mongo_db = mongo_db
        self._mongo_client = MongoClient(self._mongo_addr)

    @classmethod
    def from_config(cls, config):
        return cls(config.get("dedup_mongo_addr"),
                   config.get("dedup_mongo_db", "wsp"))

    async def handle_request(self, request):
        req = extract_request(request)
        tbl = self._mongo_client[self._mongo_db]["dedup_" % req.task_id]
        url = "%s %s" % (request.method, request.url)
        res = tbl.find_one({"url": url})
        if res is not None:
            log.debug("In task %s, the request (%s) is duplicate" % (req.task_id, url))
            raise IgnoreRequest()
        tbl.insert_one({"url": url})
