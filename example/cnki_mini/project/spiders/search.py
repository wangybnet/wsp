# coding=utf-8

import re
from html import parser

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest


class SearchSpider(BaseSpider):

    detail_match = re.compile(r"""<li class=""><a href="(.*?)">""")
    page_match = re.compile(r"""<a href="(.*?)">\[([\u4e00-\u9fa5]+)\]""")

    def parse(self, response):
        url = response.url
        if url.find("wap.cnki.net/acasearch.aspx") >= 0:
            return self._parse(response)
        return ()

    def _parse(self, response):
        print("SearchSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        for u in self.detail_match.findall(html):
            yield HttpRequest("http://wap.cnki.net/%s" % parser.unescape(u).strip())
        for t in self.page_match.findall(html):
            if len(t[1]) == 3:
                yield HttpRequest("http://wap.cnki.net/%s" % parser.unescape(t[0]).strip())

    def start_requests(self, start_urls):
        key_words = []
        for i in range(24):
            key_words.append(chr(0x41 + i))
            key_words.append(chr(0x61 + i))
        for i in range(10):
            key_words.append(chr(0x30 + i))
        types = ["CJFDTOTAL", "CPFDTOTAL", "CDMDTOTAL"]
        for k in key_words:
            for t in types:
                yield HttpRequest("http://wap.cnki.net/acasearch.aspx?q=%s&library=%s&p=1" % (t, k))
