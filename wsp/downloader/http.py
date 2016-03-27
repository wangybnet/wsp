# coding=utf-8


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
        callback: 请求成功时的回掉函数
        errback: 请求出错时的回掉函数
        meta: 放一些配置信息
    """
    def __init__(self, url, method="GET", *, proxy=None, params=None, headers=None, body=None, cookies=None, callback=None, errback=None, meta=None):
        self.url = url
        self.method = method
        self.proxy = proxy
        self.params = params
        self.headers = headers
        self.body = body
        self.cookies = cookies
        self.callback = callback
        self.errback = errback
        self._meta = dict(meta) if meta else None

    @property
    def meta(self):
        if self._meta is None:
            self._meta = {}
        return self._meta


class HttpResponse:
    """
    Http Response
        status: 整数，状态码
        headers: 字典，HTTP头
        body: 字节数组，HTTP body
        cookies: Cookie
    """
    def __init__(self, status, *, headers=None, body=None, cookies=None):
        self.status = status
        self.headers = headers
        self.body = body
        self.cookies = cookies


class HttpError(Exception):
    def __init__(self, error):
        self.erro = error
        super(HttpError, self).__init__(error)
