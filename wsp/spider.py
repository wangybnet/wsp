# coding=utf-8

import inspect
import logging

from .config import TaskConfig
from .http import HttpRequest
from .utils.config import load_object
from .middleware import MiddlewareManager

log = logging.getLogger(__name__)


class Spider:

    @classmethod
    async def crawl(cls, spiders, response, *, middleware=None):
        try:
            if middleware:
                await cls._handle_input(response, middleware)
            res = []
            for spider in spiders:
                for r in spider.parse(response):
                    if inspect.iscoroutine(r):
                        r = await r
                    if r:
                        res.append(r)
            if middleware:
                res = await cls._handle_output(response, res, middleware)
        except Exception as e:
            try:
                if middleware:
                    await cls._handle_error(response, e, middleware)
            except Exception:
                pass
            return ()
        else:
            return res

    @classmethod
    async def start_requests(cls, spiders, start_urls, *, middleware=None):
        try:
            res = []
            for spider in spiders:
                for r in spider.start_requests(start_urls):
                    if inspect.iscoroutine(r):
                        r = await r
                    if r:
                        res.append(r)
            if middleware:
                res = await cls._handle_start_requests(res, middleware)
        except Exception:
            log.warning("Unexpected error occurred when generating start requests", exc_info=True)
            return ()
        else:
            return res

    @staticmethod
    async def _handle_input(response, middleware):
        for method in middleware.input_handlers:
            res = await method(response)
            assert res is None, "Input handler must return None, got '%s'" % type(res)

    @classmethod
    async def _handle_output(cls, response, result, middleware):
        for method in middleware.output_handlers:
            result = await method(response, result)
            assert cls._isiterable(result), "Response handler must return an iterable object, got '%s'" % type(result)
        return result

    @staticmethod
    async def _handle_error(response, error, middleware):
        for method in middleware.error_handlers:
            res = await method(response, error)
            assert res is None, "Exception handler must return None, got '%s'" % type(res)

    @classmethod
    async def _handle_start_requests(cls, result, middleware):
        for method in middleware.start_requests_handlers:
            result = await method(result)
            assert cls._isiterable(result), "Start requests handler must return an iterable object, got '%s'" % type(result)
        return result

    @staticmethod
    def _isiterable(obj):
        return hasattr(obj, "__iter__")


class BaseSpider:
    """
    Spider的基类
    """

    """
    从Http Response中提取数据，或者通过提取链接生成新的Http Request

    返回一个可迭代对象，每次迭代得到的可以是Http Request，None，其他提取出来的数据。
    特别的，每次迭代得到的可以是协程（以“asnyc def”定义的函数）。
    """
    def parse(self, response):
        raise NotImplementedError

    def start_requests(self, start_urls):
        return () if start_urls is None else (HttpRequest(u) for u in start_urls)


class SpiderFactory:

    @staticmethod
    def create(config):
        spider_list = config.get(TaskConfig.SPIDERS, [])
        if not isinstance(spider_list, list):
            spider_list = [spider_list]
        log.debug("Spider list: %s" % spider_list)
        spiders = []
        for cls_path in spider_list:
            try:
                spider_cls = load_object(cls_path)
                if hasattr(spider_cls, "from_config"):
                    spider = spider_cls.from_config(config)
                else:
                    spider = spider_cls()
                assert isinstance(spider, BaseSpider), "Custom spider must extend %s" % BaseSpider.__name__
            except Exception:
                log.warning("An error occurred when loading spider '%s'" % cls_path, exc_info=True)
            else:
                spiders.append(spider)
        return spiders


class SpiderMiddlewareManager(MiddlewareManager):
    """
    Spider中间件管理器
    """

    def __init__(self, *middlewares):
        self._input_handlers = []
        self._output_handlers = []
        self._error_handlers = []
        self._start_requests_handlers = []
        MiddlewareManager.__init__(self, *middlewares)

    def _add_middleware(self, middleware):
        if hasattr(middleware, "handle_input"):
            self._input_handlers.append(middleware.handle_input)
        if hasattr(middleware, "handle_output"):
            self._output_handlers.append(middleware.handle_output)
        if hasattr(middleware, "handle_error"):
            self._error_handlers.append(middleware.handle_error)
        if hasattr(middleware, "handle_start_requests"):
            self._start_requests_handlers.append(middleware.handle_start_requests)

    @property
    def input_handlers(self):
        return self._input_handlers

    @property
    def output_handlers(self):
        return self._output_handlers

    @property
    def error_handlers(self):
        return self._error_handlers

    @property
    def start_requests_handlers(self):
        return self._start_requests_handlers

    @classmethod
    def _middleware_list_from_config(cls, config):
        mw_list = config.get(TaskConfig.SPIDER_MIDDLEWARES, [])
        if not isinstance(mw_list, list):
            mw_list = [mw_list]
        log.debug("Spider middleware list: %s" % mw_list)
        return mw_list
