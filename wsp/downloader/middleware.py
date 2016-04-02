# coding=utf-8

import logging

from wsp.middleware import MiddlewareManager
from wsp.config import task as tc

log = logging.getLogger(__name__)


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
        mw_list = config.get(tc.DOWNLOADER_MIDDLEWARES)
        if not isinstance(mw_list, list):
            mw_list = [mw_list]
        log.debug("Downloader middleware list: %s" % mw_list)
        return mw_list
