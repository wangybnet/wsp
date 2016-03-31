# coding=utf-8

import re

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest


class SearchSpider(BaseSpider):

    def __init__(self):
        self._part_url = "s.wanfangdata.com.cn/Paper.aspx"
        self._match = re.compile(r"""<a class="title" href='(.*?)' target=""")

    def parse(self, response):
        url = response.url
        return self._parse(response) if url.find(self._part_url) >= 0 else ()

    def _parse(self, response):
        print("SearchSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        return (HttpRequest(url) for url in self._match.findall(html))

    def start_requests(self, start_urls):

        def filter_urls(urls):
            for u in urls:
                if u.find(self._part_url) >= 0:
                    yield u

        return super(SearchSpider, self).start_requests(filter_urls(start_urls))
