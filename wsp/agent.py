# coding=utf-8

import asyncio
import threading
import logging
import json

from aiohttp import web

from .config import AgentConfig

log = logging.getLogger(__name__)


class Agent:

    def __init__(self, agent_config):
        assert isinstance(agent_config, AgentConfig), "Wrong configuration"
        self._config = agent_config
        self._proxy_queue = FixedLenQueue(self._config.proxy_queue_size)
        self._backup_queue = FixedLenQueue(self._config.backup_queue_size)
        self._in_queue = set()
        self._proxy_fail_times = 1
        self._backup_fail_times = 3
        self._data_lock = threading.Lock()

    def start(self):
        self._start_server()
        self._start_spider()
        self._start_checker()
        self._start_scheduler()

    def _start_server(self):
        def _start():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            app = web.Application(logger=log)
            app.router.add_resource("/http-proxy").add_route("GET", self._get_http_proxy_list)
            app.router.add_resource("/http-proxy/{number:\d*}").add_route("GET", self._get_http_proxy_list)
            host, port = self._config.agent_server_addr.split(":")
            port = int(port)
            loop.run_until_complete(loop.create_server(app.make_handler(access_log=None), host, port))
            try:
                loop.run_forever()
            except Exception:
                loop.close()

        t = threading.Thread(target=_start)
        t.start()

    def _start_spider(self):
        pass

    def _start_checker(self):
        pass

    def _start_scheduler(self):
        pass

    async def _get_http_proxy_list(self, request):
        n = request.match_info.get("number")
        res = []
        with self._data_lock:
            total = len(self._proxy_queue)
            if not n:
                n = total
            else:
                n = int(n)
                if total < n:
                    n = total
            i = 1
            while i <= n:
                res.append(self._proxy_queue[-i])
                i += 1
        return web.Response(body=json.dumps(res).encode("utf-8"))


class FixedLenQueue:

    def __init__(self, size):
        self._size = size
        self._q = [None] * (size + 1)
        self._si = self._ei = 0

    def __len__(self):
        if self._si <= self._ei:
            return self._ei - self._si
        return self._size + 1 - self._si + self._ei

    def __getitem__(self, item):
        n = len(self)
        if n == 0:
            return None
        i = self._si + item % n
        if self._si > self._size:
            i -= self._size + 1
        return self._q[i]

    def push(self, item):
        if not self.is_full():
            self._q[self._ei] = item
            self._ei = self._next(self._ei)

    def pop(self):
        if len(self) > 0:
            self._si = self._next(self._si)

    def is_full(self):
        return self._next(self._ei) == self._si

    def _next(self, index):
        if index == self._size:
            return 0
        return index + 1


class _ProxyStatus:

    def __init__(self, addr, fail=0):
        self.addr = addr
        self.fail = fail
