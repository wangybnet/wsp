# coding=utf-8

import logging
import threading

import aiohttp

from wsp.http import HttpRequest, HttpResponse, HttpError
from .asyncthread import AsyncThread
from wsp import errors

log = logging.getLogger(__name__)


class Downloader:

    def __init__(self, clients):
        self._downloader = AsyncThread()
        self._clients = threading.Semaphore(clients)

    """
    添加下载任务

    在未启动下载线程之前添加下载任务会自动启动下载线程。
    """
    def add_task(self, request, callback, *, middleware=None):
        self._clients.acquire()
        self._downloader.add_task(self._handle(request, callback, middleware=middleware))

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
            if not isinstance(e, errors.ERRORS):
                log.warning("Unexpected error occurred in downloader", exc_info=True)
            try:
                res = None
                if middleware:
                    res = await self._handle_error(request, e, middleware)
            except Exception as _e:
                if not isinstance(_e, errors.ERRORS):
                    log.warning("Unexpected error occurred when handling error in downloader", exc_info=True)
                await callback(request, _e)
            else:
                if res:
                    await callback(request, res)
                else:
                    await callback(request, e)
        else:
            await callback(request, res)
        finally:
            self._clients.release()

    @staticmethod
    async def _handle_request(request, middleware):
        for method in middleware.request_handlers:
            res = await method(request)
            assert res is None or isinstance(res, (HttpRequest, HttpResponse)), \
                "Request handler must return None, HttpRequest or HttpResponse, got '%s'" % type(res)
            if res:
                return res

    @staticmethod
    async def _handle_response(request, response, middleware):
        for method in middleware.response_handlers:
            res = await method(request, response)
            assert res is None or isinstance(res, HttpRequest), \
                "Response handler must return None or HttpRequest, got '%s'" % type(res)
            if res:
                return res

    @staticmethod
    async def _handle_error(request, error, middleware):
        for method in middleware.error_handlers:
            res = await method(request, error)
            assert res is None or isinstance(res, HttpRequest), \
                "Exception handler must return None or HttpRequest, got '%s'" % type(res)
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
