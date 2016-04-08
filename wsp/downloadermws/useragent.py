# coding=utf-8

import logging

from bson import ObjectId

from wsp.utils.parse import extract_request


log = logging.getLogger(__name__)


class UserAgentMiddleware:
    """
    给Http请求添加User-Agent的中间件
    """

    def __init__(self, user_agent, is_random):
        self._user_agent = user_agent
        self._is_random = is_random

    @classmethod
    def from_config(cls, config):
        return cls(config.get("user-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64)"),
                   config.get("random-user-agent", False))

    """
    给请求添加代理
    """
    async def handle_request(self, request):
        req = extract_request(request)
        user_agent = self._user_agent
        if self._is_random:
            user_agent = "%s %s" % (user_agent, ObjectId())
        log.debug("Assign User-Agent '%s' to request (id=%s, url=%s)" % (user_agent, req.id, request.url))
        request.headers["User-Agent"] = user_agent
