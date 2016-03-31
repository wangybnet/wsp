# coding=utf-8

import logging

from wsp.utils.fetcher import text_from_http_body
from wsp.errors import AccessDeny, ResponseNotMatch

log = logging.getLogger(__name__)


class CheckMiddleware:
    """
    判断爬虫是否被封
    """
    def __init__(self, check):
        self._check = check

    @classmethod
    def from_config(cls, config):
        return cls(config.get("check", []))

    async def handle_response(self, request, response):
        html = text_from_http_body(response)
        if html:
            flg_match = False
            flg_deny = False
            for ch in self._check:
                if "url" in ch and response.url.startswith(ch['url']):
                    if "succ" in ch and html.find(ch['succ']) >= 0:
                        flg_match = True
                        break
                    if "deny" in ch and html.find(ch['deny']) >= 0:
                        flg_deny = True
                        break
            if not flg_match:
                if flg_deny:
                    raise AccessDeny()
                else:
                    raise ResponseNotMatch()
