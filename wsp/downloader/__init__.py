# coding=utf-8

import logging
import threading

import aiohttp

from wsp.http import HttpRequest, HttpResponse, HttpError
from .asyncthread import AsyncThread
from .middleware import DownloaderMiddlewareManager

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
    def add_task(self, request, callback, *, middleware=None):
        ok = False
        with self._clients_lock:
            if self._clients > 0:
                self._clients -= 1
                ok = True
        if ok:
            self._downloader.add_task(self._handle(request, callback, middleware=middleware))
        return ok

    """
    停止下载线程
    """
    def stop(self):
        self._downloader.stop()

    async def _handle(self, request, callback, *, middleware=None):
        try:
            res = await self._handle_request(request, middleware) if middleware else None
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
            if middleware:
                _res = await self._handle_response(request, res, middleware)
                if _res:
                    res = _res
        except Exception as e:
            log.debug("An %s error occurred when downloader running: %s" % (type(e), e))
            try:
                res = None
                if middleware:
                    res = await self._handle_error(request, e, middleware)
            except Exception as _e:
                log.debug("Another %s error occurred when handling %s error: %s" % (type(_e), type(e), _e))
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
    async def _handle_request(request, middleware):
        for method in middleware.request_handlers:
            res = await method(request)
            assert res is None or isinstance(res, (HttpRequest, HttpResponse)), \
                "Request handler must return None, HttpRequest or HttpResponse, got %s" % type(res)
            if res:
                return res

    @staticmethod
    async def _handle_response(request, response, middleware):
        for method in middleware.response_handlers:
            res = await method(request, response)
            assert res is None or isinstance(res, HttpRequest), \
                "Response handler must return None or HttpRequest, got %s" % type(res)
            if res:
                return res

    @staticmethod
    async def _handle_error(request, error, middleware):
        for method in middleware.error_handlers:
            res = await method(request, error)
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
