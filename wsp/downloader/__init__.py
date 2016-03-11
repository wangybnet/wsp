# coding=utf-8

import threading

import aiohttp
from aiohttp.client_reqrep import helpers
try:
    import cchardet as chardet
except ImportError:
    import chardet

from .asyncthread import AsyncThread


class Downloader(object):

    def __init__(self, *, clients=1):
        self._downloader = AsyncThread()
        self._clients = clients
        self._clients_lock = threading.Lock()

    """
    添加下载任务，在未启动下载线程之前添加下载任务会自动启动下载线程

    request: 字典，可以包含以下字段
        method: 字符串，GET, POST, etc.
        headers: 字典，HTTP headers
        url: 字符串，URL
        params: 字典，参数
        cookies: Cookie
        proxy: 字符串，代理地址，仅支持HTTP代理，proxy需要以"http://"开头

    callback: 下载任务结束后的回调函数，会传入request和response两个函数

    response: 字典，可以包含以下字段
        status: 整数，状态码
        headers: 字典，HTTP头
        body: 字节数组，HTTP body
        text: 字符串，如果HTTP body的MIME类型是“text/*”会有该字段
        cookies: Cookie
        error: 字符串，如果请求不成功会有该字段

    返回True表示已添加该下载任务，False表示当前已经满负荷，请过段时间再添加任务
    """
    def add_task(self, request, callback):
        ok = False
        self._clients_lock.acquire()
        if self._clients > 0:
            self._clients -= 1
            ok = True
        self._clients_lock.release()
        if ok:
            self._downloader.add_task(self._run(request, callback))
        return ok

    """
    启动下载线程
    """
    def start(self):
        self._downloader.start()

    """
    停止下载线程
    """
    def stop(self):
        self._downloader.stop()

    async def _run(self, request, callback):
        response = await self._download(request)
        callback(request, response)
        self._clients_lock.acquire()
        self._clients += 1
        self._clients_lock.release()

    @staticmethod
    async def _download(request):
        with aiohttp.ClientSession(connector=None if (request.get("proxy", None) is None) else aiohttp.ProxyConnector(proxy=request["proxy"]),
                                   cookies=request.get("cookies", None)) as session:
            try:
                async with session.request("GET" if (request.get("method", None) is None) else request["method"],
                                           request["url"],
                                           headers=request.get("headers", None),
                                           params=request.get("params", None)) as resp:
                    body = await resp.read()
            except Exception as e:
                response = {"error": "%s" % e}
            else:
                response = {"status": resp.status,
                            "headers": resp.headers,
                            "body": body,
                            "cookies": resp.cookies}
                ctype = resp.headers.get("Content-Type", "").lower()
                mtype, _, _, params = helpers.parse_mimetype(ctype)
                if mtype == "text":
                    encoding = params.get("charset")
                    if not encoding:
                        encoding = chardet.detect(body)["encoding"]
                    if not encoding:
                        encoding = "utf-8"
                    response["text"] = body.decode(encoding)
        return response
