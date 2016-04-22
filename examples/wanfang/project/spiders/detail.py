# coding=utf-8

import re
from html import parser

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest


class DetailSpider(BaseSpider):

    search_match = re.compile(r"""<a href="(.*?)">""")

    def parse(self, response):
        url = response.url
        if url.find("d.wanfangdata.com.cn") >= 0:
            return self._parse(response)
        return ()

    def _parse(self, response):
        # print("DetailSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        for u in self.search_match.findall(html):
            if u.find("http://s.wanfangdata.com.cn/Paper.aspx") >= 0:
                yield HttpRequest(parser.unescape(u).strip())

    def start_requests(self, start_urls):
        return ()
