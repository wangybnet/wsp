# coding=utf-8

import aiohttp
import asyncio
import threading


class Downloader(object):
    def __init__(self):
        self._loop = None

    # 添加下载任务
    def add_task(self, request=None, callback=None):
        if (request is None) or (callback is None):
            return
        if self._loop is None:
            self.start()
        self._loop.call_soon_threadsafe(_add_task, *(request, callback))

    # 启动下载线程
    def start(self):
        if self._loop is not None:
            return

        self._loop = asyncio.new_event_loop()
        t = threading.Thread(target=_run_event_loop, name=Downloader.__name__, args=(self._loop,))
        t.start()

    # 停止下载线程
    def stop(self):
        self._loop.call_soon_threadsafe(_stop_event_loop)
        self._loop = None


def _add_task(request, callback):
    loop = asyncio.get_event_loop()
    loop.create_task(_download(request, callback))


async def _download(request, callback):
    with aiohttp.ClientSession(connector=None if (request.proxy is None) else aiohttp.ProxyConnector(proxy=request.proxy)) as session:
        try:
            async with session.get(request.url) as resp:
                html = await resp.text()

                # TODO: 对象实例化
                class Object(object):
                    pass
                response = Object()
                response.headers = resp.headers
                response.html = html

                callback(request, response)
        except "Exception":
            callback(request, None)


def _run_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
    loop.close()


def _stop_event_loop():
    loop = asyncio.get_event_loop()
    loop.stop()
