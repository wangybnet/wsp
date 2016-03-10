# coding=utf-8

from wsp.downloader import Downloader


def save_result(request, response):
    if response is None:
        print("Error")
    else:
        print("Status:", response["status"])
        print("Headers:", response["headers"])
        print("Cookies:", response["cookies"])
        print("Body:")
        print(response["body"])


if __name__ == "__main__":
    d = Downloader()

    class Object(object):
        pass
    request = {"proxy":None, "url": "http://www.baidu.com.com"}
    for i in range(5):
        d.add_task(request, save_result)
