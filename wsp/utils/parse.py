# coding=utf-8

from aiohttp.client_reqrep import helpers

from wsp.fetcher.request import WspRequest
from wsp.fetcher.response import WspResponse
from wsp import reqmeta


# WspRequest --> HttpRequest
def pack_request(wsp_request):
    req = wsp_request.http_request
    req.meta[reqmeta.WSP_REQUEST] = wsp_request
    return req


# HttpRequest --> WspRequest
# 获取WspRequest同时修改引用
def unpack_request(http_request):
    req = http_request.meta[reqmeta.WSP_REQUEST]
    http_request.meta.pop(reqmeta.WSP_REQUEST)
    return req


# HttpRequest --> WspRequest
# 获取WspRequest但是不修改引用
def extract_request(http_request):
    return http_request.meta[reqmeta.WSP_REQUEST]


# HttpRequest --> WspRequest
def parse_request(wsp_request, http_request):
    if reqmeta.WSP_REQUEST in http_request.meta:
        http_request.meta.pop(reqmeta.WSP_REQUEST)
    req = WspRequest(father_id=wsp_request.father_id,
                     task_id=wsp_request.task_id,
                     http_request=wsp_request.http_request)
    return req


# HttpResponse --> WspResponse
def parse_response(wsp_request, http_response):
    res = WspResponse(req_id=wsp_request.id,
                      task_id=wsp_request.task_id,
                      html=text_from_http_body(http_response),
                      http_response=http_response)
    return res


# Error --> WspResponse
def parse_error(wsp_request, error):
    res = WspResponse(req_id=wsp_request.id,
                      task_id=wsp_request.task_id,
                      error="%s" % error)
    return res


# Http body --> text
def text_from_http_body(http_response):
    if http_response.body is not None:
        ctype = http_response.headers.get("Content-Type", "").lower()
        mtype, _, _, params = helpers.parse_mimetype(ctype)
        if mtype == "text":
            encoding = params.get("charset")
            # if not encoding:
            #     encoding = chardet.detect(resp.body)["encoding"]
            if not encoding:
                encoding = "utf-8"
            return http_response.body.decode(encoding)
