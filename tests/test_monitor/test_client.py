# coding=utf-8

import time
import asyncio

from wsp.monitor.client import MonitorClient


class TimeHandler:

    async def fetch_data(self):
        await asyncio.sleep(1)
        t = time.time()
        fmt_t = time.strftime("%b.%d,%Y %H:%M:%S")
        print(fmt_t)
        return {"key": "timed task", "time": t, "fmt_time": fmt_t}


if __name__ == "__main__":
    client = MonitorClient("127.0.0.1:8080")
    data = {"key": "call directly", "value": "Hello, World!"}
    print("Send data:", data)
    client.report(data)
    time.sleep(1)
    handler_id = client.add_handler(TimeHandler())
    time.sleep(3.5)
    client.remove_handler(handler_id)
    time.sleep(1)
    print("Close client")
    client.close()
    print("Closed")
