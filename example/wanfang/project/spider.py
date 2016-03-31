# coding=utf-8

from wsp.spider import BaseSpider


class WanFangSpider(BaseSpider):

    def parse(self, response):
        yield "Hello, World!"
