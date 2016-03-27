# coding=utf-8


class WspRequest:

    def __init__(self, **kw):
        self.id = kw.get("id", None)
        self.father_id = kw.get("father_id", None)
        self.task_id = kw.get("task_id", None)
        self.url = kw.get("url", None)
        self.level = kw.get("level", 1)
        if self.level is not None:
            self.level = int(self.level)
        self.retry = kw.get("retry", 0)
        if self.retry is not None:
            self.retry = int(self.retry)
        self.proxy = kw.get("proxy", None)
        self.fetcher = kw.get("fetcher", None)
        self.headers = kw.get("headers", None)

    def to_dict(self):
        return {'id': self.id,
                'father_id': self.father_id,
                'task_id': self.task_id,
                'url': self.url,
                'level': self.level,
                'retry': self.retry,
                'proxy': self.proxy,
                'fetcher': self.fetcher}
