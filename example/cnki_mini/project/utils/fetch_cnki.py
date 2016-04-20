# coding=utf-8

import logging
import time
import asyncio
from urllib import parse

import aiohttp


async def fetch_search_page(keyword):
    date_str = time.strftime("%a %b %d %Y %H:%M:%S GMT%z")
    request_url = "http://epub.cnki.net/KNS/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.11&PageName=ASP.brief_default_result_aspx&DbPrefix=SCDB&DbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&db_opt=CJFQ%2CCJFN%2CCDFD%2CCMFD%2CCPFD%2CIPFD%2CCCND%2CCCJD%2CHBRD&txt_1_sel=FT%24%25%3D%7C&txt_1_value1=" + parse.quote(keyword) + "&txt_1_special1=%25&his=0&parentdb=SCDB&__=" + parse.quote(date_str)
    with aiohttp.ClientSession() as session:
        async with session.request("GET",
                                   request_url) as resp:
            body = await resp.read()
    cookies = resp.cookies
    sub_url = body.decode(encoding="utf-8")
    search_url = "http://epub.cnki.net/kns/brief/brief.aspx?pagename=" + sub_url + "&t=" + str(int(time.time())) +"&keyValue=" + parse.quote(keyword) + "&S=1"
    print(search_url)
    with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.request("GET",
                                   search_url) as resp:
            # print(resp.cookies)
            cookies.update(resp.cookies)
            body = await resp.read()
            with open("D:/cnki_search.html", "wb") as f:
                f.write(body)
    page_url = "http://epub.cnki.net/kns/brief/brief.aspx?curpage=2&RecordsPerPage=20&QueryID=0&ID=&turnpage=1&tpagemode=L&dbPrefix=SCDB&Fields=&DisplayMode=listmode&PageName=ASP.brief_default_result_aspx#J_ORDER"
    with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.request("GET",
                                   page_url) as resp:
            body = await resp.read()
            with open("D:/cnki_page.html", "wb") as f:
                f.write(body)

async def fetch_detail_page(url):
    with aiohttp.ClientSession() as session:
        async with session.request("GET",
                                   url) as resp:
            body = await resp.read()
            # print(resp.cookies)
            with open("D:/cnki_detail.html", "wb") as f:
                f.write(body)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger("wsp")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_search_page("域名"))
    loop.run_until_complete(fetch_detail_page("http://www.cnki.net/KCMS/detail/detail.aspx?filename=NJRB20150629A070&dbname=CCNDLAST2015&dbcode=CCND"))
