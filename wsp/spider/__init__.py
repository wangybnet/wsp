# coding=utf-8

import inspect
import logging

from wsp.config import task as tc
from wsp.http import HttpRequest
from wsp.utils.config import load_object
from wsp import errors

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
            if not isinstance(e, errors.ERRORS):
                log.warning("Unexpected error occurred when crawling", exc_info=True)
            try:
                if middleware:
                    await cls._handle_error(response, e, middleware)
            except Exception as _e:
                if not isinstance(_e, errors.ERRORS):
                    log.warning("Unexpected error occurred when handling the error occurred when crawling", exc_info=True)
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

    @staticmethod
    def _isiterable(obj):
        return hasattr(obj, '__iter__')


class BaseSpider:
    """
    Spider的基类
    """

    """
    从Http Response中提取数据，或者通过提取链接生成新的Http Request

    返回一个可迭代对象，每次迭代得到的可以是Http Request，None，其他提取出来的数据。
    特别的，每次迭代得到的可以是协程（以“asnyc def”定义的函数），因此在Spider中实际上是支持协程的。
    """
    def parse(self, response):
        raise NotImplementedError

    def start_requests(self, start_urls):
        return () if start_urls is None else (HttpRequest(u) for u in start_urls)


class SpiderFactory:

    @staticmethod
    def create(config):
        spider_list = config.get(tc.SPIDERS, [])
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
