# coding=utf-8

from wsp.spider import BaseSpider
from wsp.http import HttpRequest


class SearchSpider(BaseSpider):

    url_prefix = """http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber="""

    def parse(self, response):
        return ()

    def start_requests(self, start_urls):
        # > 7300000
        for i in range(0, 1000000):
            k = i + 1
            yield HttpRequest("%s%s" % (self.url_prefix, k))
