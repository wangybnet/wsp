# coding=utf-8

import aiohttp
import asyncio
import threading


class Downloader(object):

    def __init__(self, *, clients=1):
        self._loop = None
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
        html: 如果HTTP body是一个网页，会有该字段
        cookies: Cookie

    返回True表示已添加该下载任务，False表示当前已经满负荷，请过段时间再添加任务
    """
    def add_task(self, request, callback):
        if self._loop is None:
            self.start()
        ok = False
        self._clients_lock.acquire()
        if self._clients > 0:
            self._clients -= 1
            ok = True
        self._clients_lock.release()
        if ok:
            self._loop.call_soon_threadsafe(self._add_task, *(request, callback))
        return ok

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

    def _add_task(self, request, callback):
        loop = asyncio.get_event_loop()
        loop.create_task(self._download(request, callback))

    async def _download(self, request, callback):
        with aiohttp.ClientSession(connector=None if (request.get("proxy", None) is None) else aiohttp.ProxyConnector(proxy=request["proxy"]),
                                   cookies=request.get("cookies", None)) as session:
            try:
                async with session.request("GET" if (request.get("method", None) is None) else request["method"],
                                           request["url"],
                                           headers=request.get("headers", None),
                                           params=request.get("params", None)) as resp:
                    body = await resp.read()
            except Exception as e:
                print(e)
                callback(request, None)
            else:
                response = {"status": resp.status, "headers": resp.headers, "body": body, "cookies": resp.cookies}
                callback(request, response)
            finally:
                self._clients_lock.acquire()
                self._clients += 1
                self._clients_lock.release()

    @staticmethod
    def _run_event_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
        loop.close()

    @staticmethod
    def _stop_event_loop():
        loop = asyncio.get_event_loop()
        loop.stop()
