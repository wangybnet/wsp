# coding=utf-8

from wsp.middleware import MiddlewareManager
from wsp.config import task as tc


class DownloaderMiddlewareManager(MiddlewareManager):
    """
    下载器中间件管理器
    """

    def __init__(self, *middlewares):
        self._request_handlers = []
        self._response_handlers = []
        self._error_handlers = []
        super(DownloaderMiddlewareManager, self).__init__(*middlewares)

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
        return config.get(tc.DOWNLOADER_MIDDLEWARES)
