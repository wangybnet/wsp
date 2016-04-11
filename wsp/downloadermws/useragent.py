# coding=utf-8

import logging

from wsp.utils.parse import extract_request


log = logging.getLogger(__name__)


class UserAgentMiddleware:
    """
    给Http请求添加User-Agent的中间件
    """

    def __init__(self, user_agent, is_random):
        self._user_agent = user_agent
        self._is_random = is_random
        self._rand = -1

    @classmethod
    def from_config(cls, config):
        return cls(config.get("user_agent", "Mozilla/5.0 (compatible; WSP/1.0)"),
                   config.get("random_user_agent", False))

    """
    给请求添加代理
    """
    async def handle_request(self, request):
        req = extract_request(request)
        user_agent = self._user_agent
        if self._is_random:
            user_agent = "%s RAND/%s" % (user_agent, self._random())
        log.debug("Assign User-Agent '%s' to request (id=%s, url=%s)" % (user_agent, req.id, request.url))
        request.headers["User-Agent"] = user_agent

    def _random(self):
        self._rand += 1
        if self._rand > 999999:
            self._rand = 0
        return self._rand
