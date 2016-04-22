# coding=utf-8

from wsp.downloadermws.retry import RetryMiddleware as WspRetryMiddleware


class RetryMiddleware(WspRetryMiddleware):

    async def handle_response(self, request, response):
        if response.status != 200:
            return self._retry(request, "http status=%s" % response.status)
        if response.url.find("//wap.cnki.net") < 0:
            return self._retry(request, "not in 'wap.cnki.net'")
