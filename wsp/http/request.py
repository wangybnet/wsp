# coding=utf-8


class HttpRequest:
    """
    HttpRequest
        url: 字符串，URL
        method: 字符串，GET, POST, etc.
        proxy: 字符串，代理地址，仅支持HTTP代理，proxy需要以"http://"开头
        headers: 字典，HTTP头
        body: 字节数组，HTTP body
        cookies: Cookie
        meta: 放一些配置信息
    """
    def __init__(self, url, method="GET", *, proxy=None, headers=None, body=None, cookies=None, meta=None):
        self.url = url
        self.method = method
        self.proxy = proxy
        self.headers = headers
        if self.headers is None:
            self.headers = {}
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
        for x in ["url", "method", "proxy", "headers", "body", "cookies", "meta"]:
            kw.setdefault(x, getattr(self, x))
        return HttpRequest(**kw)
