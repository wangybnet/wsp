# coding=utf-8

import time
import asyncio

from wsp.monitor.server import MonitorServer


class PrintHandler:

    def __init__(self):
        self._last_time = None

    def handle_data(self, data, addr):
        print("Data:", data)
        print("Addr:", addr)
        if "time" in data:
            self._last_time = data["time"]

    async def inspect(self):
        await asyncio.sleep(3)
        if self._last_time:
            t = time.time()
            if t - self._last_time > 3:
                print("Alarm")
            else:
                print("Normal")


if __name__ == "__main__":
    server = MonitorServer("127.0.0.1:8080")
    server.start(PrintHandler())
    time.sleep(20)
    print("Stop server")
    server.stop()
    print("Server stopped")
