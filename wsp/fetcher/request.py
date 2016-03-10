# coding=utf-8


class WspRequest:

    def __init__(self, *, url=None, obj_id=None, father_id=None, task_id=None, level=1, retry=0, proxy=None, fetcher=None):
        self.obj_id = obj_id
        self.father_id = father_id
        self.task_id = task_id
        self.url = url
        self.level = level
        self.retry = retry
        self.proxy = proxy
        self.fetcher = fetcher
        if self.proxy is None:
            self.update_proxy()

    """
    将Downloader的request转换成WSP的request
    """
    @classmethod
    def from_downloader_request(cls, request):
        # TODO
        pass

    """
    将WSP的request转换成Downloader的request
    """
    def to_downloader_request(self):
        # TODO
        pass

    """
    提供一个更新代理的方法
    """
    def update_proxy(self):
        # TODO
        pass
