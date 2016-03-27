# coding=utf-8

import logging

from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.utils.fetcher import reconvert_response

log = logging.getLogger(__name__)


class PersistencePlugin:
    """
    将抓取的结果持久化
    """
    def __init__(self, addr, mongo_addr):
        self._addr = addr
        client = MongoClient(mongo_addr)
        self.db = client.wsp

    async def handle_response(self, request, response):
        req, res = reconvert_response(request, response)
        res.id = ObjectId()
        tid = '%s' % req.task_id
        resTable = self.db['result_' + tid]
        res_record = {'id': ObjectId(), 'req': req.to_dict(), 'resp': res.to_dict()}
        log.debug("Save result record (id=%s, req_url=%s) of the task %s into mongo" % (res_record["id"],
                                                                                        res_record["req"]["url"],
                                                                                        req.task_id))
        resTable.save(res_record)
