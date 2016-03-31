# coding=utf-8

from . import reqmeta


class HttpRequest:
    """
    HttpRequest
        url: 字符串，URL
        method: 字符串，GET, POST, etc.
        proxy: 字符串，代理地址，仅支持HTTP代理，proxy需要以"http://"开头
        headers: 字典，HTTP头
        body: 字节数组，HTTP body
        params: 字典，参数
        cookies: Cookie
        meta: 放一些配置信息
    """
    def __init__(self, url, method="GET", *, proxy=None, params=None, headers=None, body=None, cookies=None, meta=None):
        self.url = url
        self.method = method
        self.proxy = proxy
        self.params = params
        self.headers = headers
        self.body = body
        self.cookies = cookies
        self._meta = dict(meta) if meta else None

    @property
    def meta(self):
        if self._meta is None:
            self._meta = {}
        return self._meta

    def copy(self):
        kw = {}
        for x in ["url", "method", "proxy", "params", "headers", "body", "cookies", "meta"]:
            kw.setdefault(x, getattr(self, x))
        req = HttpRequest(**kw)
        for k in req.meta.keys():
            if k.startswith(reqmeta.META_PREFIX):
                req.meta.pop(k)
        return req


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


class HttpError(Exception):
    def __init__(self, error):
        self.error = error
        super(HttpError, self).__init__(error)
