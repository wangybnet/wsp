# coding=utf-8

import json
import asyncio
import threading
import logging

log = logging.getLogger(__name__)


class MonitorServer:

    def __init__(self, addr):
        self._addr = addr
        self._loop = None
        self._transport = None
        self._protocol = None
        self._handler_id = 0
        self._handler_id_lock = threading.Lock()
        self._handlers = {}
        self._handle_data_methods = {}

    def stop(self):
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._stop)

    def add_handler(self, handler):
        self._ensure_start()
        handler_id = self._request_handler_id()
        self._loop.call_soon_threadsafe(self._add_handler, handler_id, handler)
        return handler_id

    def remove_handler(self, handler_id):
        self._ensure_start()
        self._loop.call_soon_threadsafe(self._remove_handler, handler_id)

    def _data_received(self, data, addr):
        for method in self._handle_data_methods.values():
            method(data, addr)

    def _request_handler_id(self):
        with self._handler_id_lock:
            handler_id = self._handler_id
            self._handler_id += 1
        return handler_id

    def _add_handler(self, handler_id, handler):
        self._handlers[handler_id] = handler
        if hasattr(handler, "handle_data"):
            self._handle_data_methods[handler_id] = handler.handle_data
        if hasattr(handler, "inspect"):
            self._add_inspect_task(handler_id, handler.inspect)

    def _add_inspect_task(self, handler_id, coro_func):
        asyncio.ensure_future(self._inspect_task(handler_id, coro_func))

    async def _inspect_task(self, handler_id, coro_func):
        while handler_id in self._handlers:
            await coro_func()

    def _remove_handler(self, handler_id):
        if handler_id in self._handle_data_methods:
            self._handle_data_methods.pop(handler_id)
        self._handlers.pop(handler_id)

    def _ensure_start(self):
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            host, port = self._addr.split(":")
            port = int(port)
            listen = self._loop.create_datagram_endpoint(_MonitorServerProtocol,
                                                         local_addr=(host, port))
            self._transport, self._protocol = self._loop.run_until_complete(listen)
            self._protocol.set_callback(self._data_received)
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

    def _stop(self):
        self._transport.close()


class _MonitorServerProtocol(asyncio.DatagramProtocol):

    def __init__(self):
        self._callback = None

    def set_callback(self, callback):
        self._callback = callback

    def datagram_received(self, data, addr):
        data = json.loads(data.decode("utf-8"))
        if self._callback:
            self._callback(data, addr)

    def connection_lost(self, exc):
        log.debug("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()
