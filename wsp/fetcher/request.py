# coding=utf-8


class WspRequest:

    def __init__(self, **kw):
        self.id = kw.get("id", None)
        self.father_id = kw.get("father_id", None)
        self.task_id = kw.get("task_id", None)
        self.url = kw.get("url", None)
        self.level = kw.get("level", 1)
        self.retry = kw.get("retry", 0)
        self.proxy = kw.get("proxy", None)
        self.fetcher = kw.get("fetcher", None)
        self.headers = kw.get("headers", None)

        # TODO: 获取本机ip地址给fetcher
