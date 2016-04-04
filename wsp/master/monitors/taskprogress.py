# coding=utf-8

import asyncio


class TaskProgressMonitor:

    def __init__(self, inspect_time):
        self._inspect_time = inspect_time

    def handle_data(self, data, addr):
        pass
        # TODO

    async def inspect(self):
        await asyncio.sleep(self._inspect_time)
        # TODO
