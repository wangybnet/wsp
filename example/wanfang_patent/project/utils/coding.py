# coding=utf-8


def sanitize_url(url):
    url = url.replace("&amp;", "&")
    return url
