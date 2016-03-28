# coding=utf-8

import threading
import logging

import aiohttp

from .asyncthread import AsyncThread
from .http import HttpRequest, HttpResponse, HttpError
from .plugin import DownloaderPluginManager

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
    def add_task(self, request, callback, *, plugin=None):
        ok = False
        with self._clients_lock:
            if self._clients > 0:
                self._clients -= 1
                ok = True
        if ok:
            self._downloader.add_task(self._handle(request, callback, plugin=plugin))
        return ok

    """
    停止下载线程
    """
    def stop(self):
        self._downloader.stop()

    async def _handle(self, request, callback, *, plugin=None):
        try:
            res = await self._handle_request(request, plugin) if plugin else None
            if isinstance(res, HttpRequest):
                await callback(request, res)
                return
            if res is None:
                try:
                    response = await self._download(request)
                    log.debug("Http Response: %s %s" % (response.url, response.status))
                except Exception as e:
                    log.debug("Http Error: %s" % e)
                    raise HttpError(e)
                else:
                    res = response
            if plugin:
                _res = await self._handle_response(request, res, plugin)
                if _res:
                    res = _res
        except Exception as e:
            log.debug("An error=%s has occurred when downloader running" % e)
            try:
                res = None
                if plugin:
                    res = await self._handle_error(request, e, plugin)
            except Exception as _e:
                log.debug("Another error=%s has occurred when handling error=%s" % (e, _e))
                await callback(request, _e)
            else:
                if res:
                    await callback(request, res)
                else:
                    await callback(request, e)
        else:
            await callback(request, res)
        finally:
            with self._clients_lock:
                self._clients += 1

    @staticmethod
    async def _handle_request(request, plugin):
        for method in plugin.request_handlers:
            res = await method(request=request)
            assert res is None or isinstance(res, (HttpRequest, HttpResponse)), \
                "Request handler must return None, HttpRequest or HttpResponse, got %s" % type(res)
            if res:
                return res

    @staticmethod
    async def _handle_response(request, response, plugin):
        for method in plugin.response_handlers:
            res = await method(request=request, response=response)
            assert res is None or isinstance(res, HttpRequest), \
                "Response handler must return None or HttpRequest, got %s" % type(res)
            if res:
                return res

    @staticmethod
    async def _handle_error(request, error, plugin):
        for method in plugin.error_handlers:
            res = await method(request=request, error=error)
            assert res is None or isinstance(res, HttpRequest), \
                "Exception handler must return None or HttpRequest, got %s" % type(res)
            if res:
                return res

    @staticmethod
    async def _download(request):
        log.debug("Http Request: %s %s" % (request.method, request.url))
        with aiohttp.ClientSession(connector=None if (request.proxy is None) else aiohttp.ProxyConnector(proxy=request.proxy),
                                   cookies=request.cookies) as session:
            async with session.request(request.method,
                                       request.url,
                                       params=request.params,
                                       headers=request.headers,
                                       data=request.body) as resp:
                body = await resp.read()
                response = HttpResponse(resp.url,
                                        resp.status,
                                        headers=resp.headers,
                                        body=body,
                                        cookies=resp.cookies)
        return response
