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

    def report(self, data):
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            host, port = self._server_addr.split(":")
            port = int(port)
            connect = self._loop.create_datagram_endpoint(lambda: MonitorClientProtocol(),
                                                          remote_addr=(host, port))
            self._transport, self._protocol = self._loop.run_until_complete(connect)
            t = threading.Thread(target=self._start, args=(self._loop,))
            t.start()
        self._loop.call_soon_threadsafe(self._report, data)

    def close(self):
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._close)

    def _start(self, loop):
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            self._loop = None
            self._transport.close()
            loop.close()

    def _report(self, data):
        self._transport.sendto(json.dumps(data).encode("utf-8"))

    def _close(self):
        self._transport.close()


class MonitorClientProtocol(asyncio.DatagramProtocol):

    def connection_lost(self, exc):
        log.debug("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()
