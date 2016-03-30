# coding=utf-8

import logging
import inspect

from wsp.config import task as tc
from wsp.utils.config import load_object
from wsp.downloader.http import HttpRequest

log = logging.getLogger(__name__)


class Spider:

    @classmethod
    async def crawl(cls, spider, request, response, *, plugin=None):
        try:
            if plugin:
                await cls._handle_input(request, response, plugin)
            res = []
            for r in spider.parse(request, response):
                if inspect.iscoroutine(r):
                    r = await r
                if r:
                    res.append(r)
        except Exception as e:
            log.debug("An error=%s has occurred when spider running" % e)
            try:
                if plugin:
                    await cls._handle_error(request, response, e, plugin)
            except Exception as _e:
                log.debug("Another error=%s has occurred when handling error=%s" % (e, _e))
        else:
            return res

    @staticmethod
    async def _handle_input(request, response, plugin):
        for method in plugin.input_handlers:
            res = await method(request, response)
            assert res is None, "Input handler must return None, got %s" % type(res)

    @classmethod
    async def _handle_output(cls, request, response, result, plugin):
        for method in plugin.output_handlers:
            res = await method(request, response, result)
            assert cls._isiterable(result), "Response handler must return an iterable object, got %s" % type(res)
            return res

    @staticmethod
    async def _handle_error(request, response, error, plugin):
        for method in plugin.error_handlers:
            res = await method(request, response, error)
            assert res is None, "Exception handler must return None, got %s" % type(res)

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
    def parse(self, request, response):
        raise NotImplementedError

    def start_requests(self, start_urls):
        if hasattr(self, tc.START_URLS):
            start_urls = getattr(self, tc.START_URLS)
        for url in start_urls:
            yield HttpRequest(url)


class SpiderFactory:

    @staticmethod
    def create(config):
        cls_path = config.get(tc.SPIDER)
        try:
            spider_cls = load_object(cls_path)
            if hasattr(spider_cls, "from_config"):
                spider = spider_cls.from_config(config)
            else:
                spider = spider_cls()
            assert isinstance(spider, BaseSpider), "Custom spider must extend %s" % BaseSpider.__name__
        except Exception as e:
            log.warning("An error occurred when loading spider '%s': %s" % (cls_path, e))
            spider = None
        return spider
