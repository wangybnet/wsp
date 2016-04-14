# coding=utf-8

import re

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest

from ..utils.coding import sanitize_url


class SearchSpider(BaseSpider):

    url_prefix = """http://s.wanfangdata.com.cn/Paper.aspx?q=0&f=top&p="""

    part_url = "s.wanfangdata.com.cn/Paper.aspx"
    match_detail = re.compile(r"""<a class="title" href='(.*?)' target=""")

    def parse(self, response):
        url = response.url
        return self._parse(response) if url.find(self.part_url) >= 0 else ()

    def _parse(self, response):
        # print("SearchSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        for u in self.match_detail.findall(html):
            yield HttpRequest(sanitize_url(u))

    def start_requests(self, start_urls):
        # 823494
        for i in range(1):
            k = i + 1
            yield HttpRequest("%s%s" % (self.url_prefix, k))
