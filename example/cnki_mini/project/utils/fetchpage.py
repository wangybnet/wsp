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
    d = Downloader(clients=200, timeout=30)
    cnt = 0
    tot = 5
    d.add_task(new_http_request("../../sample_page/cnki-search.html",
                                "http://wap.cnki.net/acasearch.aspx?q=%E7%A4%BE%E4%BA%A4%E7%BD%91%E7%BB%9C&p=3"),
               save_result)
    d.add_task(new_http_request("../../sample_page/cnki-search-not-found.html",
                                "http://wap.cnki.net/acasearch.aspx?q=abcdefghijklmno&p=1"),
               save_result)
    d.add_task(new_http_request("../../sample_page/cnki-detail.html",
                                "http://wap.cnki.net/qikan-DNZS200924205.html"),
               save_result)
    d.add_task(new_http_request("../../sample_page/cnki-detail-not-found.html",
                                "http://wap.cnki.net/qikan-DNZS200924210.html"),
               save_result)
    d.add_task(new_http_request("../../sample_page/cnki-huiyi.html",
                                "http://wap.cnki.net/huiyi-QGJS200908001.html"),
               save_result)