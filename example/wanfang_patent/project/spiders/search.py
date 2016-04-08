# coding=utf-8

import re

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest

from ..utils.coding import sanitize_url


class SearchSpider(BaseSpider):

    def __init__(self):
        self._part_url = "s.wanfangdata.com.cn/patent.aspx"
        self._match_detail = re.compile(r"""<a class="title" href='(.*?)' target=""")
        self._url_prefix = """http://s.wanfangdata.com.cn/patent.aspx?q=%E5%A4%A7%E6%95%B0%E6%8D%AE+%E4%B8%93%E5%88%A9%E7%B1%BB%E5%9E%8B%3a%E5%8F%91%E6%98%8E%E4%B8%93%E5%88%A9&f=PatentType&p="""

    def parse(self, response):
        url = response.url
        return self._parse(response) if url.find(self._part_url) >= 0 else ()

    def _parse(self, response):
        print("SearchSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        for u in self._match_detail.findall(html):
            yield HttpRequest(sanitize_url(u))
        page = None
        url = response.url
        try:
            k = url.rindex("=")
            page = int(url[k + 1:])
        except Exception:
            pass
        if page:
            yield HttpRequest("%s%s" % (self._url_prefix, page + 1))
            if page > 1:
                yield HttpRequest("%s%s" % (self._url_prefix, page - 1))

    def start_requests(self, start_urls):
        for i in range(258):
            k = i * 100 + 1
            yield HttpRequest("%s%s" % (self._url_prefix, k))
