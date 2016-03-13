# coding=utf-8

import time
import asyncio

import aiohttp
from aiohttp.client_reqrep import helpers


def save_result(request, response):
    print("Cost Time: %f" % (time.time() - request["_time"]))
    if "error" in response:
        print("Error:", response["error"])
    else:
        print("URL:", request["url"], "Status:", response["status"])


async def download(request):
    begin = time.time()
    with aiohttp.ClientSession(connector=None if (request.get("proxy", None) is None) else aiohttp.ProxyConnector(proxy=request["proxy"]),
                                   cookies=request.get("cookies", None)) as session:
        try:
            async with session.request("GET" if (request.get("method", None) is None) else request["method"],
                                       request["url"],
                                       headers=request.get("headers", None),
                                       data=request.get("body", None),
                                       params=request.get("params", None)) as resp:
                body = await resp.read()
        except Exception as e:
            response = {"error": "%s" % e}
        else:
            response = {"status": resp.status,
                        "headers": resp.headers,
                        "body": body,
                        "cookies": resp.cookies}
            ctype = resp.headers.get("Content-Type", "").lower()
            mtype, _, _, params = helpers.parse_mimetype(ctype)
            if mtype == "text":
                encoding = params.get("charset")
                if not encoding:
                    encoding = "utf-8"
                response["text"] = body.decode(encoding)
    end = time.time()
    print("Duration: %f" % (end - begin))
    return response


async def delay():
    await asyncio.sleep(10)
    loop = asyncio.get_event_loop()
    loop.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for i in range(100):
        for url in ["http://www.youdao.com", "http://www.haosou.com", "http://www.iie.ac.cn"]:
            req = {"proxy": None, "url": url}
            loop.create_task(download(req))
    loop.run_until_complete(delay())