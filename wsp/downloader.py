# coding=utf-8

import asyncio
import logging
import threading

import aiohttp

from .config import TaskConfig
from .middleware import MiddlewareManager
from .http import HttpRequest, HttpResponse, HttpError

log = logging.getLogger(__name__)


class Downloader:

    def __init__(self, clients, timeout):
        self._downloader = AsyncThread()
        self._clients = threading.Semaphore(clients)
        self._timeout = timeout

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
                    log.debug("Http Error (%s): %s" % (type(e), e))
                    raise HttpError(e)
                else:
                    res = response
            if middleware:
                _res = await self._handle_response(request, res, middleware)
                if _res:
                    res = _res
        except Exception as e:
            try:
                res = None
                if middleware:
                    res = await self._handle_error(request, e, middleware)
            except Exception as _e:
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

    async def _download(self, request):
        log.debug("Http Request: %s %s" % (request.method, request.url))
        with aiohttp.ClientSession(connector=None if (request.proxy is None) else aiohttp.ProxyConnector(proxy=request.proxy),
                                   cookies=request.cookies) as session:
            with aiohttp.Timeout(self._timeout):
                async with session.request(request.method,
                                           request.url,
                                           headers=request.headers,
                                           data=request.body) as resp:
                    body = await resp.read()
        response = HttpResponse(resp.url,
                                resp.status,
                                headers=resp.headers,
                                body=body,
                                cookies=resp.cookies)
        return response


class AsyncThread:

    def __init__(self):
        self._loop = None

    def stop(self):
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._stop)

    def add_task(self, coro):
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            t = threading.Thread(target=self._start, args=(self._loop,))
            t.start()
        self._loop.call_soon_threadsafe(self._add_task, coro)

    def _start(self, loop):
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            self._loop = None
            loop.close()

    @staticmethod
    def _stop():
        loop = asyncio.get_event_loop()
        loop.stop()

    @staticmethod
    def _add_task(coro):
        asyncio.ensure_future(coro)


class DownloaderMiddlewareManager(MiddlewareManager):
    """
    下载器中间件管理器
    """

    def __init__(self, *middlewares):
        self._request_handlers = []
        self._response_handlers = []
        self._error_handlers = []
        MiddlewareManager.__init__(self, *middlewares)

    def _add_middleware(self, middleware):
        if hasattr(middleware, "handle_request"):
            self._request_handlers.append(middleware.handle_request)
        if hasattr(middleware, "handle_response"):
            self._response_handlers.append(middleware.handle_response)
        if hasattr(middleware, "handle_error"):
            self._error_handlers.append(middleware.handle_error)

    @property
    def request_handlers(self):
        return self._request_handlers

    @property
    def response_handlers(self):
        return self._response_handlers

    @property
    def error_handlers(self):
        return self._error_handlers

    @classmethod
    def _middleware_list_from_config(cls, config):
        mw_list = config.get(TaskConfig.DOWNLOADER_MIDDLEWARES, [])
        if not isinstance(mw_list, list):
            mw_list = [mw_list]
        log.debug("Downloader middleware list: %s" % mw_list)
        return mw_list
