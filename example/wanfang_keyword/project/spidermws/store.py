# coding=utf-8

import os
import time

from bson import ObjectId


class StoreMiddleware:

    def __init__(self):
        self._match_url = "d.wanfangdata.com.cn"
        self._store_path = "/datastore/wsp/wanfang"
        if not os.path.exists(self._store_path):
            os.makedirs(self._store_path, 0o775)

    async def handle_input(self, response):
        print("Response url: %s" % response.url)
        if response.url.find(self._match_url) >= 0:
            self._store(response)

    def _store(self, response):
        objid = "%s" % ObjectId()
        html_file = "%s/%s.html" % (self._store_path, objid)
        meta_file = "%s/%s.meta" % (self._store_path, objid)
        with open(html_file, "wb") as f:
            f.write(response.body)
        with open(meta_file, "wb") as f:
            f.write(("%s" % time.time()).encode("utf-8"))
            f.write(response.url.encode("utf-8"))
