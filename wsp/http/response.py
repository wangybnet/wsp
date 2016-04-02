# coding=utf-8


class HttpResponse:
    """
    Http Response
        url: 字符串，URL
        status: 整数，状态码
        headers: 字典，HTTP头
        body: 字节数组，HTTP body
        cookies: Cookie
    """
    def __init__(self, url, status, *, headers=None, body=None, cookies=None, request=None):
        self.url = url
        self.status = status
        self.headers = headers
        self.body = body
        self.cookies = cookies
        self.request = request

    @property
    def meta(self):
        if self.request:
            return self.request.meta
        return None

    def copy(self):
        kw = {}
        for x in ["url", "status", "headers", "body", "cookies", "request"]:
            kw.setdefault(x, getattr(self, x))
        return HttpResponse(**kw)
