# coding=utf-8

import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.utils.fetcher import parse_response, extract_request

log = logging.getLogger(__name__)


class MongoStoreMiddleware:
    """
    将抓取的结果持久化
    """
    def __init__(self, mongo_addr, mongo_db):
        self._mongo_addr = mongo_addr
        self._mongo_db = mongo_db
        self._mongo_client = MongoClient(mongo_addr)

    @classmethod
    def from_config(cls, config):
        return cls(config.get("store_mongo_addr"),
                   config.get("store_mongo_db", "wsp"))

    async def handle_response(self, request, response):
        req = extract_request(request)
        res = parse_response(req, response)
        res_table = self._mongo_client[self._mongo_db]["result_%s" % req.task_id]
        res_obj_id = ObjectId()
        res_record = {'_id': res_obj_id, 'id': "%s" % res_obj_id, 'req': req.to_dict(), 'resp': res.to_dict()}
        log.debug("Save result record (id=%s, req_id=%s, req_url=%s) of the task %s into mongo" % (res_record["id"],
                                                                                                   res_record["req"]["id"],
                                                                                                   res_record["req"]["http_request"]["url"],
                                                                                                   req.task_id))
        res_table.save(res_record)
