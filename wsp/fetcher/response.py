# coding=utf-8


class WspResponse:

    def __init__(self, **kw):
        self.id = kw.get("id", None)
        self.req_id = kw.get("req_id", None)
        self.task_id = kw.get("task_id", None)
        self.html = kw.get("html", None)
        self.error = kw.get("error", None)
        self.http_response = kw.get("http_response", None)

    def to_dict(self):
        return {
            'id': self.id,
            'req_id': self.req_id,
            'task_id': self.task_id,
            'html': self.html,
            'error': self.error,
            'http_response': None if self.http_response is None else {
                'url': self.http_response.url,
                'http_code': self.http_response.status
            }}
