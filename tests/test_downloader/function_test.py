# coding=utf-8

import time

from wsp.downloader import Downloader
from wsp.downloader.http import HttpRequest, HttpError


def _convert(func):
    def wrapper(req, resp):
        return func(req, resp)
    return wrapper


@_convert
def save_result(request, response):
    if isinstance(response, HttpError):
        print("Error:", response.error)
    else:
        print("URL:", request.url)
        print("Status:", response.status)
        print("Headers:", response.headers)
        print("Cookies:", response.cookies)
        print("Body:")
        print(response.body)


if __name__ == "__main__":
    d = Downloader(clients=2)
    for url in ["https://github.com", "http://www.haosou.com", "http://error-domain-0x00.com", "http://www.baidu.com.com", "http://www.iie.ac.cn"]:
        req = HttpRequest(url)
        ok = False
        while not ok:
            ok = d.add_task(req, save_result)
            if ok:
                break
            else:
                print("Downloader is busy, so it cannot handle %s" % url)
            time.sleep(1)
    time.sleep(5)
    d.stop()