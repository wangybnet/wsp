# coding=utf-8


class WspResponse:

    def __init__(self, *, id=None, req_id=None, task_id=None, url=None, html=None, http_code=200, error=None):
        self.id = id
        self.req_id = req_id
        self.task_id = task_id
        self.url = url
        self.html = html
        self.http_code = http_code
        self.error = error
