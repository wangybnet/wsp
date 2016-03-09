# coding=utf-8

from wsp.downloader import Downloader


def save_result(request, response):
    print(response.headers)
    print(response.html)


if __name__ == "__main__":
    d = Downloader()

    class Object(object):
        pass
    request = Object()
    request.proxy = None
    request.url = "http://www.baidu.com.com"
    for i in range(5):
        d.add_task(request, save_result)
