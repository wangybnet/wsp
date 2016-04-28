# coding=utf-8

import random
import asyncio
import logging
import math

import aiohttp

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
        self._update_slot = 1

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
        proxy = await self._pick_proxy()
        log.debug("Assign proxy '%s' to request (url=%s)" % (proxy, request.url))
        request.proxy = proxy

    async def _pick_proxy(self):
        while True:
            await self._update_proxy_list()
            if self._proxy_list:
                break
            await asyncio.sleep(self._update_time)
        n = len(self._proxy_list)
        k = random.randint(1, n * n)
        k = int(math.sqrt(k)) - 1
        proxy = self._proxy_list[k]
        if not proxy.startswith("http://"):
            proxy = "http://%s" % proxy
        return proxy

    async def _update_proxy_list(self):
        if self._update_slot > 0:
            self._update_slot -= 1
            log.debug("Updating proxy list")
            try:
                with aiohttp.ClientSession() as session:
                    async with session.get(self._agent_addr) as resp:
                        json = await resp.json()
                        proxy_list = json["result"]
                        if proxy_list:
                            self._proxy_list = proxy_list
            except Exception:
                pass
            finally:
                asyncio.ensure_future(self._update_slot_delay())

    async def _update_slot_delay(self):
        await asyncio.sleep(self._update_time)
        self._update_slot += 1
