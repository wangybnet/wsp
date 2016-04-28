# coding=utf-8

from aiohttp.client_reqrep import helpers


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
