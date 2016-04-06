# coding=utf-8

from wsp.errors import AccessDeny, ResponseNotMatch, IgnoreRequest
from wsp.http import HttpError
from wsp.utils.parse import extract_request


class RetryMiddleware:
    """
    判断是否重试
    """

    # 需要重试的异常的集合
    RETRY_ERRORS = (HttpError, AccessDeny, ResponseNotMatch)

    def __init__(self, max_retry_times):
        self._max_retry_times = max_retry_times

    @classmethod
    def from_config(cls, config):
        return cls(config.get("max_retry_times", 5))

    async def handle_response(self, request, response):
        if response.status != 200:
            return self._retry(request, "http status=%s" % response.status)

    async def handle_error(self, request, error):
        if not isinstance(error, self.RETRY_ERRORS):
            return
        return self._retry(request, "%s: %s" % (type(error), error))

    def _retry(self, request, reason):
        req = extract_request(request)
        retry_times = request.meta.get("_retry_times", 0) + 1
        if retry_times <= self._max_retry_times:
            request.meta["_retry_times"] = retry_times
            return request.copy()
        else:
            raise IgnoreRequest()
