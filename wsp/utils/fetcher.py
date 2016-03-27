# coding=utf-8

from aiohttp.client_reqrep import helpers

from wsp.downloader.http import HttpRequest
from wsp.fetcher.response import WspResponse
from wsp import reqmeta


# WspRequest --> HttpRequest
def convert_request(request):
    req = HttpRequest(request.url, proxy=request.proxy, headers=request.headers)
    req.meta[reqmeta.WSP_REQUEST] = request
    return req


# HttpRequest --> WspRequest
def reconvert_request(request):
    return request.meta[reqmeta.WSP_REQUEST]


# HttpRequest, HttpResponse --> WspRequest, WspResponse
def reconvert_response(request, response):
    req = reconvert_request(request)
    res = WspResponse(req_id=request.id,
                      task_id=request.task_id,
                      url=request.url)
    res.html = text_from_http_body(response)
    res.url = req.url
    res.http_code = response.status
    res.headers = response.headers
    res.body = response.body
    return req, res


# HttpRequest, Error --> WspRequest, WspResponse
def reconvert_error(request, error):
    req = reconvert_request(request)
    res = WspResponse(req_id=request.id,
                      task_id=request.task_id,
                      url=request.url)
    res.error = "%s" % error
    return req, res


# Http body --> text
def text_from_http_body(response):
    if response.body is not None:
        ctype = response.headers.get("Content-Type", "").lower()
        mtype, _, _, params = helpers.parse_mimetype(ctype)
        if mtype == "text":
            encoding = params.get("charset")
            # if not encoding:
            #     encoding = chardet.detect(resp.body)["encoding"]
            if not encoding:
                encoding = "utf-8"
            return response.body.decode(encoding)
