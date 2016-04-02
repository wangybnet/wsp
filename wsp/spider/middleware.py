# coding=utf-8

import logging

from wsp.middleware import MiddlewareManager
from wsp.config import task as tc

log = logging.getLogger(__name__)


class SpiderMiddlewareManager(MiddlewareManager):
    """
    Spider中间件管理器
    """

    def __init__(self, *middlewares):
        self._input_handlers = []
        self._output_handlers = []
        self._error_handlers = []
        MiddlewareManager.__init__(self, *middlewares)

    def _add_middleware(self, middleware):
        if hasattr(middleware, "handle_input"):
            self._input_handlers.append(middleware.handle_input)
        if hasattr(middleware, "handle_output"):
            self._output_handlers.append(middleware.handle_output)
        if hasattr(middleware, "handle_error"):
            self._error_handlers.append(middleware.handle_error)

    @property
    def input_handlers(self):
        return self._input_handlers

    @property
    def output_handlers(self):
        return self._output_handlers

    @property
    def error_handlers(self):
        return self._error_handlers

    @classmethod
    def _middleware_list_from_config(cls, config):
        mw_list = config.get(tc.SPIDER_MIDDLEWARES)
        if not isinstance(mw_list, list):
            mw_list = [mw_list]
        log.debug("Spider middleware list: %s" % mw_list)
        return mw_list
