# coding=utf-8

import time

from wsp.downloader import Downloader
from tests.test_downloader.domains import DOMAINS


def save_result(request, response):
    print("Cost Time: %f" % (time.time() - request["_time"]))
    if "error" in response:
        print("Error:", response["error"])
    else:
        print("URL:", request["url"], "Status:", response["status"])


if __name__ == "__main__":
    clients = 200
    d = Downloader(clients=clients)
    begin = time.time()
    repeat = 5
    for i in range(repeat):
        for domain in DOMAINS:
            req = {"proxy": None, "url": "http://" + domain, "_time": time.time()}
            ok = False
            while not ok:
                ok = d.add_task(req, save_result)
                if ok:
                    break
                else:
                    print("Downloader is busy, so it cannot handle %s" % domain)
                time.sleep(0.5)
    duration = time.time() - begin
    print("Duration: %f" % duration)
    print("QPS: %f" % ((len(DOMAINS) * repeat - clients) / duration))
    d.stop()
