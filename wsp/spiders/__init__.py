# coding=utf-8

from wsp.downloader.http import HttpRequest


class Spider:

    def parse(self, request, response):
        raise NotImplementedError

"""
    def start_requests(self):
        assert hasattr(self, 'start_urls'), "No start urls in spider"
        for url in self.start_urls:
            yield self.request_from_url(url)

    def request_from_url(self, url):
        return HttpRequest(url)
"""
