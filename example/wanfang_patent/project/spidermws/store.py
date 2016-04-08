# coding=utf-8

import os
import re

from wsp.utils.parse import text_from_http_body


class StoreMiddleware:

    def __init__(self):
        self._url_part = "d.wanfangdata.com.cn/Patent"
        self._store_path = "/root/wanfang_patent"
        self._store_file = "patent.txt"
        self._match_title = re.compile(r"""<h1>(.*?)</h1>""")
        self._match_text = re.compile(r"""<div class="text">(.*?)</div>""")
        if not os.path.exists(self._store_path):
            os.makedirs(self._store_path, 0o775)

    async def handle_input(self, response):
        print("Response url: %s" % response.url)
        if response.url.find(self._url_part) >= 0:
            self._store(response)

    def _store(self, response):
        try:
            html = text_from_http_body(response)
        except Exception:
            pass
        else:
            title = None
            text = None
            for t in self._match_title.findall(html):
                title = t
                break
            for t in self._match_text.findall(html):
                text = t
                break
            if title and text:
                with open("%s/%s" % (self._store_path, self._store_file), "ab") as f:
                    f.write(("%s\t%s\n" % (text, title)).encode("utf-8"))
