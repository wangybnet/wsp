# coding=utf-8

START_URLS = "start_urls"
MAX_RETRY = "max_retry"
MAX_LEVEL = "max_level"
CHECK = "check"
FOLLOW = "follow"

DEFAULT_CONFIG = {START_URLS: [],
                  MAX_RETRY: 3,
                  MAX_LEVEL: 0,
                  CHECK: [],
                  FOLLOW: {}}


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
        self.task_config = kw.get("task_config", {})
        # self.start_urls = kw.get("start_urls", ())
        # self.follow = kw.get("follow", {})
        # self.max_retry = kw.get("max_retry", DEFAULT_MAX_RETRY)
        # self.check = kw.get("check", ())
        # self.max_level = kw.get("max_level", DEFAULT_MAX_LEVEL)

    def get_config(self, name):
        name = name.lower()
        res = self.task_config.get(name)
        if not res:
            res = DEFAULT_CONFIG.get(name)
        return res
