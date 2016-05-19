# coding=utf-8

import json
import math
import random
import asyncio

import aiohttp

import socket
import struct

_socket_init = socket.socket.__init__


def socket_init(*args, **kw):
    _socket_init(*args, **kw)
    args[0].setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))


socket.socket.__init__ = socket_init


class ProxyTest:

    def __init__(self, agent_addr):
        if not agent_addr.startswith("http://"):
            agent_addr = "http://%s" % agent_addr
        self._agent_addr = agent_addr
        self._proxy_list = None
        self._update_slot = 1
        self._good = 0
        self._bad = 0

    def run(self, d):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self._stop(d))
        for i in range(100):
            asyncio.ensure_future(self._run())
        loop.run_forever()
        loop.close()
        print("good:", self._good, "bad: ", self._bad, "ratio:", 0 if self._good + self._bad == 0 else self._good / (self._good + self._bad))

    async def _stop(self, d):
        await asyncio.sleep(d)
        loop = asyncio.get_event_loop()
        loop.stop()

    async def _run(self):
        while True:
            proxy = await self._pick_proxy()
            try:
                await self._download(proxy)
            except Exception:
                self._bad += 1
            else:
                self._good += 1

    async def _download(self, proxy):
        with aiohttp.ClientSession(connector=aiohttp.ProxyConnector(proxy=proxy)) as session:
            with aiohttp.Timeout(20):
                async with session.request("GET",
                                           "https://wangyb.net") as resp:
                    body = await resp.read()

    async def _pick_proxy(self):
        while True:
            await self._update_proxy_list()
            if self._proxy_list:
                break
            await asyncio.sleep(10)
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
            try:
                with aiohttp.ClientSession() as session:
                    async with session.get(self._agent_addr) as resp:
                        body = await resp.read()
                        json_obj = json.loads(body.decode(encoding="utf-8"))
                        proxy_list = json_obj["result"]
                        if proxy_list:
                            self._proxy_list = proxy_list
            except Exception:
                print("Unexpected error occurred when updating proxy list")
            finally:
                asyncio.ensure_future(self._update_slot_delay())

    async def _update_slot_delay(self):
        await asyncio.sleep(10)
        self._update_slot += 1

if __name__ == "__main__":
    test = ProxyTest("192.168.120.181:1234")
    test.run(300)
