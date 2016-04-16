# coding=utf-8

import logging

from pymongo import MongoClient

from wsp.utils.parse import extract_request, parse_response, parse_error
from wsp.config import task as tc

log = logging.getLogger(__name__)


class MongoDumpMiddleware:
    """
    将所有的request和response都存到mongo里面用于debug
    """
    def __init__(self, mongo_addr, mongo_db, mongo_tbl_request, mongo_tbl_response):
        self._mongo_client = MongoClient(mongo_addr)
        self._request_tbl = self._mongo_client[mongo_db][mongo_tbl_request]
        self._response_tbl = self._mongo_client[mongo_db][mongo_tbl_response]

    @classmethod
    def from_config(cls, config):
        task_id = config.get(tc.TASK_ID)
        return cls(config.get("dump_mongo_addr", None),
                   config.get("dump_mongo_db", "wsp"),
                   config.get("dump_mongo_tbl_request", "request_%s" % task_id),
                   config.get("dump_mongo_tbl_response", "response_%s" % task_id))

    async def handle_request(self, request):
        req = extract_request(request)
        self._save_request(req)

    async def handle_reponse(self, request, response):
        req = extract_request(request)
        res = parse_response(req, response)
        self._save_response(res)

    async def handle_error(self, request, error):
        req = extract_request(request)
        res = parse_error(req, error)
        self._save_response(res)

    def _save_request(self, req):
        reqJson = req.to_dict()
        log.debug("Save request record (id=%s, url=%s) into mongo" % (reqJson["id"],
                                                                      reqJson["http_request"]["url"]))
        self._request_tbl.save(reqJson)

    def _save_response(self, res):
        resJson = res.to_dict()
        log.debug("Save response record (id=%s, req_id=%s) into mongo" % (resJson["id"],
                                                                          resJson["req_id"]))
        self._response_tbl.save(resJson)
