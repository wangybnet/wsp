# coding=utf-8

import json
import asyncio
import logging
import threading

log = logging.getLogger(__name__)


class MonitorClient:

    def __init__(self, server_addr, *handlers):
        self._server_addr = server_addr
        self._loop = None
        self._transport = None
        self._protocol = None
        self._fetch_data_methods = []
        for h in handlers:
            self._add_handler(h)

    def send(self, data):
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._send, data)

    def start(self):
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            host, port = self._server_addr.split(":")
            port = int(port)
            connect = self._loop.create_datagram_endpoint(lambda: _MonitorClientProtocol(),
                                                          remote_addr=(host, port))
            self._transport, self._protocol = self._loop.run_until_complete(connect)
            t = threading.Thread(target=self._start, args=(self._loop,))
            t.start()
            for method in self._fetch_data_methods:
                self._loop.call_soon_threadsafe(self._add_report_task, method)

    def stop(self):
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._stop)

    def _add_handler(self, handler):
        if hasattr(handler, "fetch_data"):
            self._fetch_data_methods.append(handler.fetch_data)

    def _add_report_task(self, coro_func):
        asyncio.ensure_future(self._report_task(coro_func))

    async def _report_task(self, coro_func):
        while True:
            data = await coro_func()
            self._send(data)

    def _send(self, data):
        self._transport.sendto(json.dumps(data).encode("utf-8"))

    def _start(self, loop):
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            self._loop = None
            self._transport.close()
            loop.close()

    def _stop(self):
        self._transport.close()


class _MonitorClientProtocol(asyncio.DatagramProtocol):

    def connection_lost(self, exc):
        log.debug("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()
