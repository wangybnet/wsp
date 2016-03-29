# coding=utf-8


class WspTask:
    def __init__(self, **kw):
        self.id = kw.get("id", None)
        self.create_time = kw.get("create_time", None)
        if self.create_time is not None:
            self.create_time = int(self.create_time)
        self.finish_time = kw.get("finish_time", None)
        if self.finish_time is not None:
            self.finish_time = int(self.finish_time)
        self.status = kw.get("status", None)
        if self.status is not None:
            self.status = int(self.status)
        self.desc = kw.get("desc", None)
