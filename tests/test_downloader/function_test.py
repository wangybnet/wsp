# coding=utf-8

import logging
import time

from wsp.downloader import Downloader
from wsp.http import HttpRequest, HttpError


async def save_result(request, response):
    if isinstance(response, HttpError):
        print("Error:", response.error)
    else:
        print("URL:", response.url)
        print("Status:", response.status)
        print("Headers:", response.headers)
        print("Cookies:", response.cookies)
        print("Body:")
        print(response.body)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    d = Downloader(clients=2, timeout=1)
    for url in ["https://github.com", "http://www.haosou.com", "http://error-domain-0x00.com", "http://www.baidu.com.com", "http://www.iie.ac.cn"]:
        req = HttpRequest(url)
        ok = False
        d.add_task(req, save_result)
    time.sleep(5)
    d.stop()
