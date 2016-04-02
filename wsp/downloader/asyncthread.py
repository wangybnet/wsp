# coding=utf-8

import asyncio
import threading


class AsyncThread:

    def __init__(self):
        self._loop = None

    def stop(self):
        if self._loop is None:
            return
        self._loop.call_soon_threadsafe(self._stop)

    def add_task(self, coro):
        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            t = threading.Thread(target=self._start, args=(self._loop,))
            t.start()
        self._loop.call_soon_threadsafe(self._add_task, coro)

    def _start(self, loop):
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            self._loop = None
            loop.close()

    @staticmethod
    def _stop():
        loop = asyncio.get_event_loop()
        loop.stop()

    @staticmethod
    def _add_task(coro):
        loop = asyncio.get_event_loop()
        loop.create_task(coro)
