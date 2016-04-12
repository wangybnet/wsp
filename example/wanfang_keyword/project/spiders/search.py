# coding=utf-8

import re

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body
from wsp.http import HttpRequest

from ..utils.coding import sanitize_url


class SearchSpider(BaseSpider):

    url_prefix = """http://s.wanfangdata.com.cn/Paper.aspx?q=%E4%BF%A1%E5%B7%A5%E6%89%80&f=top&p="""

    part_url = "s.wanfangdata.com.cn/Paper.aspx"
    match_detail = re.compile(r"""<a class="title" href='(.*?)' target=""")
    match_page = re.compile(r"""<a href="(.*?)" class="page">""")

    def parse(self, response):
        url = response.url
        return self._parse(response) if url.find(self.part_url) >= 0 else ()

    def _parse(self, response):
        print("SearchSpider parse the response(url=%s)" % response.url)
        html = text_from_http_body(response)
        has_paper = False
        for u in self.match_detail.findall(html):
            yield HttpRequest(sanitize_url(u))
            has_paper = True
        # for u in self.match_page.findall(html):
        #     yield HttpRequest("http://s.wanfangdata.com.cn/Paper.aspx%s" % sanitize_url(u))
        if has_paper:
            url = response.url
            try:
                k = url.rindex("=")
                page = int(url[k + 1:])
            except Exception:
                pass
            else:
                yield HttpRequest("%s%s" % (self.url_prefix, page + 1))
                if page > 1:
                    yield HttpRequest("%s%s" % (self.url_prefix, page - 1))

    def start_requests(self, start_urls):
        # 851
        for i in range(851):
            k = i * 100 + 1
            yield HttpRequest("%s%s" % (self.url_prefix, k))