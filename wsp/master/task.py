# coding=utf-8

from bson import ObjectId

from wsp.utils.config import ensure_int


class WspTask:

    def __init__(self, **kw):
        self.id = kw.get("id", "%s" % ObjectId())
        self.create_time = kw.get("create_time", None)
        if self.create_time is not None:
            ensure_int(self.create_time)
        self.finish_time = kw.get("finish_time", None)
        if self.finish_time is not None:
            ensure_int(self.finish_time)
        self.status = kw.get("status", None)
        if self.status is not None:
            ensure_int(self.status)
        self.desc = kw.get("desc", None)

    def to_dict(self):
        return {
            '_id': ObjectId(self.id),
            'id': self.id,
            'create_time': self.create_time,
            'finish_time': self.finish_time,
            'status': self.status,
            'desc': self.desc
        }
