# coding=utf-8


class WspResponse:

    def __init__(self, **kw):
        self.id = kw.get("id", None)
        self.req_id = kw.get("req_id", None)
        self.task_id = kw.get("task_id", None)
        self.url = kw.get("url", None)
        self.html = kw.get("html", None)
        self.http_code = kw.get("http_code", None)
        if self.http_code is not None:
            self.http_code = int(self.http_code)
        self.error = kw.get("error", None)
        self.headers = kw.get("headers", None)
        self.body = kw.get("body", None)
