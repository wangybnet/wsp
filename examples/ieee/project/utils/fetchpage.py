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
    tot = 4
    d.add_task(new_http_request("../../sample_page/ieee_xpl_abstract.html",
                                "http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=7035918"),
               save_result)
    d.add_task(new_http_request("../../sample_page/ieee_xpl_abstract_not_found.html",
                                "http://ieeexplore.ieee.org/xpl/articleDetails.jsp?arnumber=9035918"),
               save_result)
    d.add_task(new_http_request("../../sample_page/ieee_xpl_references.html",
                                "http://ieeexplore.ieee.org/xpl/abstractReferences.jsp?arnumber=7035918"),
               save_result)
    d.add_task(new_http_request("../../sample_page/ieee_xpl_references_not_found.html",
                                "http://ieeexplore.ieee.org/xpl/abstractReferences.jsp?arnumber=9035918"),
               save_result)
