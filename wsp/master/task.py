# coding=utf-8

from bson import ObjectId

TASK_CREATE = 0
TASK_RUNNING = 1
TASK_STOPPED = 2
TASK_FINISHED = 3
TASK_REMOVED = 4


class WspTask:

    def __init__(self, **kw):
        self.id = kw.get("id", "%s" % ObjectId())
        self.create_time = kw.get("create_time", None)
        self.finish_time = kw.get("finish_time", None)
        self.status = kw.get("status", None)
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
