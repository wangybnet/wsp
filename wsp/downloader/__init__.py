# coding=utf-8

import threading
import logging

import aiohttp

from .asyncthread import AsyncThread
from .http import HttpRequest, HttpResponse, HttpError

log = logging.getLogger(__name__)


class Downloader:

    def __init__(self, *, clients=1):
        self._downloader = AsyncThread()
        self._clients = clients
        self._clients_lock = threading.Lock()

    """
    添加下载任务
    在未启动下载线程之前添加下载任务会自动启动下载线程。
    返回True表示已添加该下载任务，False表示当前已经满负荷，请过段时间再添加任务。
    """
    def add_task(self, request, callback):
        ok = False
        with self._clients_lock:
            if self._clients > 0:
                self._clients -= 1
                ok = True
        if ok:
            self._downloader.add_task(self._run(request, callback))
        return ok

    """
    停止下载线程
    """
    def stop(self):
        self._downloader.stop()

    async def _run(self, request, callback):
        try:
            response = await self._download(request)
            log.debug("%s %s" % (request.url, response.status))
            callback(request, response)
        except Exception as e:
            log.debug("%s" % e)
            callback(request, HttpError(e))
        finally:
            with self._clients_lock:
                self._clients += 1

    @staticmethod
    async def _download(request):
        log.debug("%s %s" % (request.method, request.url))
        with aiohttp.ClientSession(connector=None if (request.proxy is None) else aiohttp.ProxyConnector(proxy=request.proxy),
                                   cookies=request.cookies) as session:
            async with session.request(request.method,
                                       request.url,
                                       params=request.params,
                                       headers=request.headers,
                                       data=request.body) as resp:
                body = await resp.read()
                response = HttpResponse(resp.status,
                                        headers=resp.headers,
                                        body=body,
                                        cookies=resp.cookies)
        return response
