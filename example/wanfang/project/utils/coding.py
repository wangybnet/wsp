# coding=utf-8


def sanitize_url(url):
    url = url.replace("&amp;", "&")
    return url


def url_to_utf8_str(url):
    s = []
    slot = 0
    for c in url:
        if slot > 0:
            s.append(c)
            slot -= 1
        elif c == "%":
            s.append(c)
            slot = 2
        else:
            for b in c.encode("utf-8"):
                s.append("%%%2x" % b)
    return "".join(s).lower()
