# coding=utf-8

import re

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body


class DetailSpider(BaseSpider):

    def __init__(self):
        self._part_url = "d.wanfangdata.com.cn"
        self._match = re.compile(r"""<a href="(.*?)">""")

    def parse(self, response):
        url = response.url
        return self._parse(response) if url.find(self._part_url) >= 0 else ()

    def _parse(self, response):
        html = text_from_http_body(response)
        for url in self._match.findall(html):
            if url.find("http://s.wanfangdata.com.cn/Paper.aspx") >= 0:
                yield url

    def start_requests(self, start_urls):

        def filter_urls(urls):
            for u in urls:
                if u.find(self._part_url) >= 0:
                    yield u

        return super(DetailSpider, self).start_requests(filter_urls(start_urls))
