# coding=utf-8

import re
from html import parser

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest


class SearchSpider(BaseSpider):

    detail_match = re.compile(r"""<a class="title" href='(.*?)' target=""")
    page_match = re.compile(r"""<a href="(.*?)" class="page">""")

    def parse(self, response):
        url = response.url
        if url.find("s.wanfangdata.com.cn/Paper.aspx") >= 0:
            return self._parse(response)
        return ()

    def _parse(self, response):
        print("SearchSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        for u in self.detail_match.findall(html):
            yield HttpRequest(parser.unescape(u).strip())
        for u in self.page_match.findall(html):
            yield HttpRequest("http://s.wanfangdata.com.cn/Paper.aspx%s" % parser.unescape(u).strip())

    def start_requests(self, start_urls):
        # key_words = []
        # for i in range(24):
        #     key_words.append(chr(0x41 + i))
        #     key_words.append(chr(0x61 + i))
        # for i in range(10):
        #     key_words.append(chr(0x30 + i))
        # for k in key_words:
        #     yield HttpRequest("http://s.wanfangdata.com.cn/Paper.aspx?q=%s&f=top" % k)
        yield HttpRequest("http://s.wanfangdata.com.cn/Paper.aspx?q=%E4%BF%A1%E5%B7%A5%E6%89%80&f=top")
