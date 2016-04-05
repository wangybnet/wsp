# coding=utf-8

import time
import random
import asyncio
import logging

import aiohttp

from wsp.utils.parse import extract_request

log = logging.getLogger(__name__)


class ProxyMiddleware:
    """
    给Http请求添加代理的中间件
    """

    def __init__(self, proxy_agent_addr, proxy_update_time):
        if not proxy_agent_addr.startswith("http://"):
            proxy_agent_addr = "http://%s" % proxy_agent_addr
        assert proxy_update_time > 0, "The time interval to update proxy list must be a positive number"
        self._agent_addr = proxy_agent_addr
        self._update_time = proxy_update_time
        self._proxy_list = None
        self._last_update = 0

    """
    根据任务配置实例化代理中间件
    """
    @classmethod
    def from_config(cls, config):
        return cls(config.get("proxy_agent_addr"),
                   config.get("proxy_update_time", 10))

    """
    给请求添加代理
    """
    async def handle_request(self, request):
        req = extract_request(request)
        proxy = await self._pick_proxy()
        log.debug("Assign proxy '%s' to request (id=%s, url=%s)" % (proxy, req.id, request.url))
        request.proxy = proxy

    async def _pick_proxy(self):
        while True:
            await self._update_proxy_list()
            if self._proxy_list:
                break
            await asyncio.sleep(self._update_time + 0.1)
        k = random.randint(0, len(self._proxy_list) - 1)
        proxy = self._proxy_list[k]
        if not proxy.startswith("http://"):
            proxy = "http://%s" % proxy
        return proxy

    async def _update_proxy_list(self):
        t = time.time()
        if t - self._last_update > self._update_time:
            self._last_update = t
            with aiohttp.ClientSession() as session:
                async with session.get(self._agent_addr) as resp:
                    json = await resp.json()
                    self._proxy_list = json["result"]
