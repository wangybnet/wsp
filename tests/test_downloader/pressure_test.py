# coding=utf-8

import time

from wsp.downloader import Downloader
from wsp.downloader.http import HttpRequest, HttpError
from tests.test_downloader.domains import GLOBAL_DOMAINS, CHINESE_DOMAINS


def save_result(request, response):
    print("Cost Time: %f" % (time.time() - request._time))
    if isinstance(response, HttpError):
        print("Error:", response.error)
    else:
        print("URL:", request.url, "Status:", response.status)


def test_global_sites():
    clients = 200
    d = Downloader(clients=clients)
    begin = time.time()
    repeat = 5
    for i in range(repeat):
        for domain in GLOBAL_DOMAINS:
            req = HttpRequest("http://" + domain)
            req._time = time.time()
            ok = False
            while not ok:
                ok = d.add_task(req, save_result)
                if ok:
                    break
                else:
                    print("Downloader is busy, so it cannot handle %s" % domain)
                time.sleep(1)
    duration = time.time() - begin
    print("Duration: %f" % duration)
    print("QPS: %f" % ((len(GLOBAL_DOMAINS) * repeat - clients) / duration))
    d.stop()


def test_chinese_sites():
    clients = 200
    d = Downloader(clients=clients)
    begin = time.time()
    repeat = 50
    for i in range(repeat):
        for domain in CHINESE_DOMAINS:
            req = HttpRequest("http://" + domain)
            req._time=time.time()
            ok = False
            while not ok:
                ok = d.add_task(req, save_result)
                if not ok:
                    print("Downloader is busy, so it cannot handle %s" % domain)
                    time.sleep(1)
    duration = time.time() - begin
    print("Duration: %f" % duration)
    print("QPS: %f" % ((len(CHINESE_DOMAINS) * repeat - clients) / duration))
    d.stop()


if __name__ == "__main__":
    # test_global_sites()
    test_chinese_sites()
