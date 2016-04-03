# coding=utf-8

import time

from wsp.monitor.server import MonitorServer


class PrintHandler:

    def handle_data(self, data):
        print("Data:", data)


if __name__ == "__main__":
    server = MonitorServer("127.0.0.1:8080", PrintHandler())
    print("Start server")
    server.start()
    print("Server started")
    time.sleep(20)
    print("Stop server")
    server.stop()
    print("Server stopped")
