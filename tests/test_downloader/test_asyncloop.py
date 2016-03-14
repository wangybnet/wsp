# coding=utf-8

import time

from wsp.downloader.asyncthread import AsyncThread


async def hello():
    print("Hello World!")


async def sleep():
    time.sleep(3)


if __name__ == "__main__":
    thread = AsyncThread()
    thread.add_task(sleep())
    thread.add_task(hello())
    print("Done")
    time.sleep(5)
    thread.stop()
