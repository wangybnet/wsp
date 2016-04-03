# coding=utf-8

import time

from wsp.monitor.client import MonitorClient


if __name__ == "__main__":
    client = MonitorClient("127.0.0.1:8080")
    data = [{"task_id":1, "completed":5}]
    print("Send data")
    client.report(data)
    print("Done")
    time.sleep(3)
    data = {"task_id":2, "completed":10}
    print("Send data")
    client.report(data)
    print("Done")
    time.sleep(3)
    print("Close client")
    client.close()
    print("Closed")
