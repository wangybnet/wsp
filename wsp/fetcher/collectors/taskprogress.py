# coding=utf-8

import threading
import asyncio

from bson import ObjectId


class TaskProgressCollector:
    """
    针对每个task有一个handler
    """

    def __init__(self, report_time):
        self._report_time = report_time
        self._tasks = {}
        self._pushed_count = {}
        self._pulled_count = {}
        self._data_lock = threading.Lock()

    """
    改变当前任务

    这里tasks是一个任务ID的列表
    """
    def set_tasks(self, *tasks):
        new_tasks = {}
        for t in tasks:
            if t in self._tasks:
                new_tasks[t] = self._tasks[t]
            else:
                new_tasks[t] = self._load(t)
        for t in self._tasks.keys():
            if t not in new_tasks:
                self._remove(t)
        self._tasks = new_tasks

    """
    添加任务
    """
    def add_task(self, task_id):
        if task_id not in self._tasks:
            self._tasks[task_id] = self._load(task_id)

    def record_pulled_request(self, task_id):
        if task_id in self._tasks:
            with self._data_lock:
                self._pulled_count[task_id] += 1

    def record_pushed_request(self, task_id):
        if task_id in self._tasks:
            with self._data_lock:
                self._pushed_count[task_id] += 1

    """
    获取上报数据
    """
    async def fetch_data(self):
        await asyncio.sleep(self._report_time)
        data = []
        with self._data_lock:
            for t in self._tasks.keys():
                data.append({"signature": self._tasks[t],
                             "task_id": t,
                             "pulled_count": self._pulled_count,
                             "pushed_count": self._pushed_count})
        return {"task_progress": data}

    def _load(self, task_id):
        signature = "%s" % ObjectId()
        self._pulled_count[task_id] = 0
        self._pushed_count[task_id] = 0
        return signature

    def _remove(self, task_id):
        self._pulled_count.pop(task_id)
        self._pushed_count.pop(task_id)
