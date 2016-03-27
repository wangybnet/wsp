# coding=utf-8

import logging

from wsp.utils.fetcher import text_from_http_body, reconvert_request
from wsp.downloader.http import HttpError
from wsp.errors import AccessDeny, ResponseNotMatch, IgnoreRequest
from wsp import reqmeta

log = logging.getLogger(__name__)


class RetryPlugin:
    """
    判断是否重试
    """

    # 需要重试的异常的集合
    RETRY_ERRORS = (HttpError, AccessDeny, ResponseNotMatch)
    # 需要重试的HTTP状态码的集合
    RETRY_HTTP_STATUS = (500, 502, 503, 504, 408)

    def __init__(self, max_retry_times):
        self._max_retry_times = max_retry_times

    async def handle_response(self, request, response):
        if response.status in self.RETRY_HTTP_STATUS:
            return self._retry(request, 1, "http status=%s" % response.status)

    async def process_exception(self, request, exception):
        if not isinstance(exception, self.RETRY_ERRORS):
            return
        # FIXME: 根据错误的类型确定是否占用重试次数
        slot = 1
        return self._retry(request, slot)

    def _retry(self, request, slot, reason):
        req = reconvert_request(request)
        retry_times = request.meta.get(reqmeta.RETRY_TIMES, 0) + slot
        if retry_times <= self._max_retry_times:
            log.debug("We will retry the request(id=%s, url=%s) because of %s" % (req.id, req.url, reason))
            request.meta[reqmeta.RETRY_TIMES] = retry_times
            return request
        else:
            log.debug("The WSP request(id=%s, url=%s) has been retried %d times, and it will be aborted." % (req.id, req.url, self._max_retry))
            raise IgnoreRequest()
