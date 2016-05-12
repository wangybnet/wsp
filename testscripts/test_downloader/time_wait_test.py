# coding=utf-8

import time

from wsp.downloader import Downloader
from wsp.http import HttpRequest, HttpError


async def save_result(request, response):
    print("Cost Time: %f" % (time.time() - request._time))
    if isinstance(response, HttpError):
        print("Error (%s): %s" % (type(response.error), response.error))
    else:
        print("URL:", request.url, "Status:", response.status)


def test():
    clients = 200
    d = Downloader(clients=clients, timeout=30)
    begin = time.time()
    total = 100000
    for i in range(total):
        req = HttpRequest("http://www.baidu.com")
        req._time=time.time()
        d.add_task(req, save_result)
    duration = time.time() - begin
    print("Duration: %f" % duration)
    print("QPS: %f" % ((total - clients) / duration))
    d.stop()


if __name__ == "__main__":
    test()
