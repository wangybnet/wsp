# coding=utf-8

import logging
import re

from wsp.spider import BaseSpider
from wsp.utils.parse import text_from_http_body

log = logging.getLogger(__name__)


class HrefRuleSpider(BaseSpider):
    def __init__(self, **kw):
        self._starts_with = kw.get("starts_with", [])
        self._ends_with = kw.get("ends_with", [])
        self._contains = kw.get("contains", [])
        self._regex_matches = kw.get("regex_matches", [])

    def parse(self, response):
        html = text_from_http_body(response)
        if not html:
            return []
        url_list = re.findall(r'<a[\s]*href[\s]*=[\s]*["|\']?(.*?)["|\']?>', html)
        hasNewUrl = False
        for u in url_list:
            if u.startswith('//'):
                if response.url.startswith("http:"):
                    u = 'http:' + u
                else:
                    u = 'https:' + u
            elif not u.startswith('http://') and not u.startswith("https://"):
                strlist = response.url.split('?')
                u = strlist[0] + u
            tag = False
            for rule in self._starts_with:
                if u.startswith(rule):
                    tag = True
                    break
            if not tag:
                for rule in self._ends_with:
                    if u.endswith(rule):
                        tag = True
                        break
            if not tag:
                for rule in self._contains:
                    if u.find(rule) != -1:
                        tag = True
                        break
            if not tag:
                for rule in self._regex_matches:
                    if re.search(rule, u):
                        tag = True
                        break
            if tag:
                log.debug("Find a new url %s in the page %s." % (u, response.url))
                hasNewUrl = True
                req = response.request.copy()
                req.url = u
                yield req
