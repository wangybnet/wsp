# coding=utf-8

from wsp.middleware import MiddlewareManager
from wsp.config import task as tc


class SpiderMiddlewareManager(MiddlewareManager):
    """
    Spider中间件管理器
    """

    def __init__(self, *middlewares):
        self._input_handlers = []
        self._output_handlers = []
        self._error_handlers = []
        super(SpiderMiddlewareManager, self).__init__(*middlewares)

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
        return config.get(tc.SPIDER_MIDDLEWARES)
