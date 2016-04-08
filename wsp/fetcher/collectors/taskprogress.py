# coding=utf-8

import threading
import asyncio

from bson import ObjectId

from ..config import FetcherConfig


class TaskProgressCollector:
    """
    针对每个task有一个handler
    """

    def __init__(self, local_config):
        assert isinstance(local_config, FetcherConfig), "Wrong configuration"
        self._local_config = local_config
        self._report_time = self._local_config.task_progress_report_time
        self._tasks = {}
        self._data_lock = threading.Lock()

    """
    改变当前任务

    这里tasks是一个任务ID的列表
    """
    def set_tasks(self, *tasks):
        new_tasks = {}
        with self._data_lock:
            for t in tasks:
                if t in self._tasks:
                    new_tasks[t] = self._tasks[t]
                else:
                    new_tasks[t] = _TaskProgress()
            self._tasks = new_tasks

    def record_pulled_request(self, task_id):
        with self._data_lock:
            if task_id not in self._tasks:
                self._tasks[task_id] = _TaskProgress()
            tp = self._tasks[task_id]
            tp.completed += 1
            tp.updated = True

    def record_pushed_request(self, task_id):
        with self._data_lock:
            if task_id not in self._tasks:
                self._tasks[task_id] = _TaskProgress()
            tp = self._tasks[task_id]
            tp.total += 1
            tp.updated = True

    """
    获取上报数据
    """
    async def fetch_data(self):
        await asyncio.sleep(self._report_time)
        data = []
        with self._data_lock:
            for t in self._tasks.keys():
                tp = self._tasks[t]
                if tp.updated:
                    data.append({"task_id": t,
                                 "signature": tp.signature,
                                 "completed": tp.completed,
                                 "total": tp.total})
                    tp.updated = False
        return {"task_progress": data}


class _TaskProgress:
    def __init__(self, **kw):
        self.signature = kw.get("signature", "%s" % ObjectId())
        self.completed = kw.get("completed", 0)
        self.total = kw.get("total", 0)
        self.updated = kw.get("updated", False)
