# coding=utf-8

import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.utils.parse import parse_response, extract_request
from wsp.config import task as tc

log = logging.getLogger(__name__)


class MongoStoreMiddleware:
    """
    将抓取的结果持久化
    """
    def __init__(self, mongo_addr, mongo_db, mongo_tbl):
        self._mongo_client = MongoClient(mongo_addr)
        self._result_tbl = self._mongo_client[mongo_db][mongo_tbl]

    @classmethod
    def from_config(cls, config):
        task_id = config.get(tc.TASK_ID)
        return cls(config.get("store_mongo_addr"),
                   config.get("store_mongo_db", "wsp"),
                   config.get("store_mongo_tbl", "result_%s" % task_id))

    async def handle_response(self, request, response):
        req = extract_request(request)
        res = parse_response(req, response)
        res_obj_id = ObjectId()
        res_record = {'_id': res_obj_id, 'id': "%s" % res_obj_id, 'req': req.to_dict(), 'resp': res.to_dict()}
        log.debug("Save result record (id=%s, req_id=%s, req_url=%s) of the task %s into mongo" % (res_record["id"],
                                                                                                   res_record["req"]["id"],
                                                                                                   res_record["req"]["http_request"]["url"],
                                                                                                   req.task_id))
        self._result_tbl.save(res_record)
