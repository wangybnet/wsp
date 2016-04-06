# coding=utf-8

import re

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest

from ..utils.coding import sanitize_url


class DetailSpider(BaseSpider):

    def __init__(self):
        self._part_url = "d.wanfangdata.com.cn"
        self._match = re.compile(r"""<a href="(.*?)">""")

    def parse(self, response):
        url = response.url
        return self._parse(response) if url.find(self._part_url) >= 0 else ()

    def _parse(self, response):
        print("DetailSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        for u in self._match.findall(html):
            if u.find("http://s.wanfangdata.com.cn/Paper.aspx") >= 0:
                yield HttpRequest(sanitize_url(u))

    def start_requests(self, start_urls):
        return ("http://s.wanfangdata.com.cn/Paper.aspx?q=%E4%BF%A1%E5%B7%A5%E6%89%80&f=top",
                "http://s.wanfangdata.com.cn/Paper.aspx?q=%E4%BF%A1%E5%B7%A5%E6%89%80&f=top&p=3")
