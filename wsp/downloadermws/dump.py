# coding=utf-8

import logging

from pymongo import MongoClient

from wsp.utils.fetcher import extract_request, parse_response, parse_error

log = logging.getLogger(__name__)


class MongoDumpMiddleware:
    """
    将所有的request和response都存到mongo里面用于debug
    """
    def __init__(self, mongo_addr, mongo_db):
        self._mongo_addr = mongo_addr
        self._mongo_db = mongo_db
        self._mongo_client = MongoClient(self._mongo_addr)

    @classmethod
    def from_config(cls, config):
        return cls(config.get("dump_mongo_addr", None),
                   config.get("dump_mongo_db", "wsp"))

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
        reqTable = self._mongo_client[self._mongo_db]["request_%s" % req.task_id]
        reqJson = req.to_dict()
        log.debug("Save request record (id=%s, url=%s) into mongo" % (reqJson["id"],
                                                                      reqJson["http_request"]["url"]))
        reqTable.save(reqJson)

    def _save_response(self, res):
        resTable = self._mongo_client[self._mongo_db]["response_%s" % res.req_id]
        resJson = res.to_dict()
        log.debug("Save response record (id=%s, req_id=%s) into mongo" % (resJson["id"],
                                                                          resJson["req_id"]))
        resTable.save(resJson)
