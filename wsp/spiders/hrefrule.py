# coding=utf-8

import logging
import re

from bson.objectid import ObjectId

from wsp.spiders import Spider
from wsp.utils.fetcher import convert_request, reconvert_request, text_from_http_body
from wsp.fetcher.request import WspRequest

log = logging.getLogger(__name__)


class HrefRuleSpider(Spider):
    def __init__(self, start_urls, **kw):
        self.start_urls = start_urls
        self._starts_with = kw.get("starts_with", [])
        self._ends_with = kw.get("ends_with", [])
        self._contains = kw.get("contains", [])
        self._regex_matches = kw.get("regex_matches", [])

    def parse(self, request, response):
        req = reconvert_request(request)
        html = text_from_http_body(response)
        if not html:
            return []
        url_list = re.findall(r'<a[\s]*href[\s]*=[\s]*["|\']?(.*?)["|\']?>', html)
        hasNewUrl = False
        for u in url_list:
            if u.startswith('//'):
                if req.url.startswith("http:"):
                    u = 'http:' + u
                else:
                    u = 'https:' + u
            elif not u.startswith('http://') and not u.startswith("https://"):
                strlist = req.url.split('?')
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
                log.debug("Find a new url %s in the page %s." % (u, req.url))
                hasNewUrl = True
                newReq = WspRequest()
                newReq.id = ObjectId()
                newReq.father_id = req.id
                newReq.task_id = req.task_id
                newReq.url = u
                newReq.level = req.level + 1
                yield convert_request(newReq)
