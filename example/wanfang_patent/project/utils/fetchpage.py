# coding=utf-8

import logging

import wsp
from wsp.http import HttpRequest, HttpResponse
from wsp.downloader import Downloader


async def save_result(request, response):
    assert isinstance(request, HttpRequest) and isinstance(response, HttpResponse)
    print("url: %s" % response.url)
    filename = request.meta.get("filename")
    with open(filename, "wb") as f:
        f.write(response.body)
    global cnt
    cnt += 1
    if cnt >= tot:
        d.stop()


def new_http_request(filename, url):
    req = HttpRequest(url)
    req.meta["filename"] = filename
    return req


if __name__ == "__main__":
    wsp.set_logger(logging.DEBUG,
                   "%(asctime)s %(name)s: [%(levelname)s] %(message)s",
                   "%b.%d,%Y %H:%M:%S")
    log = logging.getLogger("wsp")
    d = Downloader(clients=200)
    cnt = 0
    tot = 2
    d.add_task(new_http_request("../../sample_page/patent.html",
                                "http://d.wanfangdata.com.cn/Patent/CN201510255995.0/"),
               save_result)
    d.add_task(new_http_request("../../sample_page/search.html",
                                "http://s.wanfangdata.com.cn/patent.aspx?q=%E5%A4%A7%E6%95%B0%E6%8D%AE+%E4%B8%93%E5%88%A9%E7%B1%BB%E5%9E%8B%3a%E5%8F%91%E6%98%8E%E4%B8%93%E5%88%A9&f=PatentType&p=2"),
               save_result)
