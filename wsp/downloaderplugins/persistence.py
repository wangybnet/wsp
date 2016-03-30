# coding=utf-8

import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.utils.fetcher import parse_response, extract_request

log = logging.getLogger(__name__)


class PersistencePlugin:
    """
    将抓取的结果持久化
    """
    def __init__(self, mongo_addr, mongo_result_db, mongo_result_tbl):
        self._mongo_client = MongoClient(mongo_addr)
        self._mongo_result_db = mongo_result_db
        self._mongo_result_tbl = mongo_result_tbl

    @classmethod
    def from_config(cls, config):
        return cls(config.get("mongo_addr"),
                   config.get("mongo_result_db", "wsp"),
                   config.get("monggo_result_tbl", "result"))

    async def handle_response(self, request, response):
        req = extract_request(request)
        res = parse_response(req, response)
        res_table = self._mongo_client[self._mongo_result_db]["%s_%s" % (self._mongo_result_tbl, req.task_id)]
        res_record = {'_id': ObjectId(), 'req': req.to_dict(), 'resp': res.to_dict()}
        log.debug("Save result record (id=%s, req_url=%s) of the task %s into mongo" % (res_record["id"],
                                                                                        res_record["req"]["http_request"]["url"],
                                                                                        req.task_id))
        res_table.save(res_record)
