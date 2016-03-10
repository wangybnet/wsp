# coding=utf-8


class WspRequest:

    def __init__(self, *, id=None, father_id=None, task_id=None, url=None, level=1, retry=0, proxy=None, fetcher=None):
        self.id = id
        self.father_id = father_id
        self.task_id = task_id
        self.url = url
        self.level = level
        self.retry = retry
        self.proxy = proxy
        self.fetcher = fetcher
