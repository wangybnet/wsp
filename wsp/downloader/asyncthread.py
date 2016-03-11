# coding=utf-8

import asyncio
import threading


class AsyncThread(object):

    def __init__(self):
        self._loop = None

    def start(self):
        if self._loop is not None:
            return
        self._loop = asyncio.new_event_loop()
        t = threading.Thread(target=self._start, args=(self._loop,))
        t.start()

    def stop(self):
        self._loop.call_soon_threadsafe(self._stop)
        self._loop = None

    def add_task(self, coro):
        if self._loop is None:
            self.start()
        self._loop.call_soon_threadsafe(self._add_task, coro)

    @staticmethod
    def _start(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
        loop.close()

    @staticmethod
    def _stop():
        loop = asyncio.get_event_loop()
        loop.stop()

    @staticmethod
    def _add_task(coro):
        loop = asyncio.get_event_loop()
        loop.create_task(coro)