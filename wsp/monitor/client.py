# coding=utf-8

import json
import asyncio
import logging
import threading

log = logging.getLogger(__name__)


class MonitorClient:

    def __init__(self, server_addr):
        self._server_addr = server_addr
        self._loop = None
        self._transport = None
        self._protocol = None
        self._handler_id = 0
        self._handler_id_lock = threading.Lock()
        self._handlers = {}

    def add_handler(self, handler):
        self._ensure_start()
        handler_id = self._request_handler_id()
        self._loop.call_soon_threadsafe(self._add_handler, handler_id, handler)
        return handler_id

    def remove_handler(self, handler_id):
        self._ensure_start()
        self._loop.call_soon_threadsafe(self._remove_handler, handler_id)

    def report(self, data):
        self._ensure_start()
        self._loop.call_soon_threadsafe(self._report, data)

    def close(self):
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._close)

    def _request_handler_id(self):
        with self._handler_id_lock:
            handler_id = self._handler_id
            self._handler_id += 1
        return handler_id

    def _add_handler(self, handler_id, handler):
        self._handlers[handler_id] = handler
        if hasattr(handler, "fetch_data"):
            self._add_report_task(handler_id, handler.fetch_data)

    def _add_report_task(self, handler_id, coro_func):
        asyncio.ensure_future(self._report_task(handler_id, coro_func))

    async def _report_task(self, handler_id, coro_func):
        while handler_id in self._handlers:
            data = await coro_func()
            self._report(data)

    def _remove_handler(self, handler_id):
        if handler_id in self._handlers:
            self._handlers.pop(handler_id)

    def _report(self, data):
        self._transport.sendto(json.dumps(data).encode("utf-8"))

    def _ensure_start(self):
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            host, port = self._server_addr.split(":")
            port = int(port)
            connect = self._loop.create_datagram_endpoint(lambda: _MonitorClientProtocol(),
                                                          remote_addr=(host, port))
            self._transport, self._protocol = self._loop.run_until_complete(connect)
            t = threading.Thread(target=self._start, args=(self._loop,))
            t.start()

    def _start(self, loop):
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            self._loop = None
            self._transport.close()
            loop.close()

    def _close(self):
        self._transport.close()


class _MonitorClientProtocol(asyncio.DatagramProtocol):

    def connection_lost(self, exc):
        log.debug("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()
