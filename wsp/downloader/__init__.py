# coding=utf-8

import aiohttp
import asyncio
import threading


class Downloader(object):

    def __init__(self):
        self._loop = None

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
        html: 如果HTTP body是一个网页，会有该字段
        cookies: Cookie

    返回True表示已添加该下载任务，False表示当前已经满负荷，请过段时间再添加任务
    """
    # TODO: 控制task数量
    def add_task(self, request=None, callback=None):
        if (request is None) or (callback is None):
            return
        if self._loop is None:
            self.start()
        self._loop.call_soon_threadsafe(self._add_task, *(request, callback))

    """
    启动下载线程
    """
    def start(self):
        if self._loop is not None:
            return
        self._loop = asyncio.new_event_loop()
        t = threading.Thread(target=self._run_event_loop, args=(self._loop,))
        t.start()

    """
    停止下载线程
    """
    def stop(self):
        self._loop.call_soon_threadsafe(self._stop_event_loop)
        self._loop = None

    @classmethod
    def _add_task(cls, request, callback):
        loop = asyncio.get_event_loop()
        loop.create_task(cls._download(request, callback))

    @staticmethod
    async def _download(request, callback):
        with aiohttp.ClientSession(connector=None if (request.get("proxy", None) is None) else aiohttp.ProxyConnector(proxy=request["proxy"])) as session:
            try:
                # TODO: 添加其他参数
                async with session.request("GET" if (request.get("method", None) is None) else request["method"],
                                           request["url"]) as resp:
                    body = await resp.read()
            except Exception as e:
                print(e)
                callback(request, None)
            else:
                response = {"status": resp.status, "headers": resp.headers, "body": body, "cookies": resp.cookies}
                callback(request, response)

    @staticmethod
    def _run_event_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
        loop.close()

    @staticmethod
    def _stop_event_loop():
        loop = asyncio.get_event_loop()
        loop.stop()
