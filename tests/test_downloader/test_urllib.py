# coding=utf-8

import time
from urllib import request

from tests.test_downloader.domains import DOMAINS


if __name__ == "__main__":
    begin = time.time()
    repeat = 1
    for i in range(repeat):
        for domain in DOMAINS:
            try:
                data = request.urlopen("http://" + domain, timeout=10).read()
                data = data.decode('utf-8')
            except Exception:
                pass
    duration = time.time() - begin
    print("Duration: %f" % duration)
    print("QPS: %f" % ((len(DOMAINS) * repeat) / duration))
