# coding=utf-8

from wsp import reqmeta


class WspRequest:

    def __init__(self, **kw):
        self.id = kw.get("id", None)
        self.father_id = kw.get("father_id", None)
        self.task_id = kw.get("task_id", None)
        self.fetcher = kw.get("fetcher", None)
        self.http_request = kw.get("http_request", None)
        assert self.http_request is not None, "Must have an http request"

    def to_dict(self):
        return {
            'id': self.id,
            'father_id': self.father_id,
            'task_id': self.task_id,
            'fetcher': self.fetcher,
            'http_request': None if self.http_request is None else {
                'url': self.http_request.url,
                'level': self.http_request.meta.get(reqmeta.CRAWL_LEVEL, 0),
                'retry': self.http_request.meta.get(reqmeta.RETRY_TIMES, 0),
                'proxy': self.http_request.proxy
            }}
