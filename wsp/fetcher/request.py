# coding=utf-8

from bson.objectid import ObjectId

from wsp import reqmeta


class WspRequest:

    def __init__(self, **kw):
        self.id = kw.get("id", ObjectId())
        self.father_id = kw.get("father_id", None)
        self.task_id = kw.get("task_id", None)
        self.fetcher = kw.get("fetcher", None)
        self._http_request = kw.get("http_request", None)
        assert self._http_request is not None, "Must have an http request"

    @property
    def http_request(self):
        return self._http_request

    def to_dict(self):
        return {
            'id': self.id,
            'father_id': self.father_id,
            'task_id': self.task_id,
            'fetcher': self.fetcher,
            'http_request': {
                'url': self._http_request.url,
                'level': self._http_request.meta.get(reqmeta.CRAWL_LEVEL, 0),
                'retry': self._http_request.meta.get(reqmeta.RETRY_TIMES, 0),
                'proxy': self._http_request.proxy
            }}
