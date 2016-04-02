# coding=utf-8

import asyncio
import threading
import json
import logging

log = logging.getLogger(__name__)


class MonitorServer:
    
    def __init__(self, addr):
        self._addr = addr
        self._loop = None
        self._transport = None
        self._protocol = None

    def start(self):
        if self._loop is not None:
            return
        self._loop = asyncio.new_event_loop()
        host, port = self._addr.split(":")
        port = int(port)
        listen = self._loop.create_datagram_endpoint(MonitorServerProtocol,
                                                     local_addr=(host, port))
        self._transport, self._protocol = self._loop.run_until_complete(listen)
        t = threading.Thread(target=self._start, args=(self._loop,))
        t.start()

    def stop(self):
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._stop)

    def _stop(self):
        self._transport.close()

    def _start(self, loop):
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            self._loop = None
            self._transport.close()
            loop.close()


class MonitorServerProtocol(asyncio.DatagramProtocol):

    def __init__(self):
        self._data_handlers = []

    # NOTE: 设置handlers要确保线程安全
    def set_handlers(self, *handlers):
        self._data_handlers = []
        for h in handlers:
            if hasattr(h, "handle_data"):
                self._data_handlers.append(h.handle_data)

    def datagram_received(self, data, addr):
        data = json.loads(data.decode("utf-8"))
        log.debug("Received data: %s" % dict)
        for h in self._data_handlers:
            h.handle_data(data)

    def connection_lost(self, exc):
        log.debug("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()
