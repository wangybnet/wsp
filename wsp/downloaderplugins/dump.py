# coding=utf-8

import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.utils.fetcher import extract_request, parse_response, parse_error

log = logging.getLogger(__name__)


class DumpPlugin:
    """
    将所有的request和response都存到mongo里面用于debug
    """
    def __init__(self, mongo_addr):
        client = MongoClient(mongo_addr)
        self.db = client.wsp

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
        req.id = ObjectId()
        reqTable = self.db.request
        reqJson = req.to_dict()
        log.debug("Save request record (id=%s, url=%s) into mongo" % (reqJson["id"],
                                                                      reqJson["http_request"]["url"]))
        reqTable.save(reqJson)

    def _save_response(self, res):
        res.id = ObjectId()
        resTable = self.db.response
        resJson = res.to_dict()
        log.debug("Save response record (id=%s, url=%s) into mongo" % (resJson["id"],
                                                                       resJson["http_request"]["url"]))
        resTable.save(resJson)
