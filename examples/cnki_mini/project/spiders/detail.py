# coding=utf-8

import re
from html import parser

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest


class DetailSpider(BaseSpider):

    keyword_match = re.compile(r"""<strong><a href="(.*?)" target="_self">""")

    def parse(self, response):
        url = response.url
        if url.find("wap.cnki.net/qikan") >= 0 or url.find("wap.cnki.net/lunwen") >= 0 or url.find("wap.cnki.net/huiyi") >= 0:
            return self._parse(response)
        return ()

    def _parse(self, response):
        # print("DetailSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        for u in self.keyword_match.findall(html):
            yield HttpRequest("http://wap.cnki.net/%s" % parser.unescape(u).strip())

    def start_requests(self, start_urls):
        return ()
