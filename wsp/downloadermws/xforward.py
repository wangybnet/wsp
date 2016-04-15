# coding=utf-8

import random
import logging

from wsp.utils.parse import extract_request

log = logging.getLogger(__name__)


class XForwardMiddleware:

    async def handle_request(self, request):
        req = extract_request(request)
        x = "61.%s.%s.%s" % (random.randint(128, 191), random.randint(0, 255), random.randint(0, 255))
        log.debug("Assign 'X-Forwarded-For: %s' to request (id=%s, url=%s)" % (x, req.id, request.url))
        request.headers["X-Forwarded-For"] = x
