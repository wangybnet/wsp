# coding=utf-8

import os
import random


class StoreMiddleware:

    def __init__(self):
        self._store_path = "/home/wsp/wanfang"
        if not os.path.exists(self._store_path):
            os.makedirs(self._store_path, 0o775)

    async def handle_input(self, response):
        print("Response url: %s" % response.url)
        filename = "%s/%s.html" % (self._store_path, random.randint(0, 1000000))
        with open(filename, "wb") as f:
            f.write(response.body)
