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
    """
    def __init__(self, url, method="GET", *, proxy=None, params=None, headers=None, body=None, cookies=None):
        self.url = url
        self.method = method
        self.proxy = proxy
        self.params = params
        self.headers = headers
        self.body = body
        self.cookies = cookies


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


class HttpError:
    """
    Http Error
        error: 请求失败时的产生的错误
    """
    def __init__(self, error):
        self.error = error
