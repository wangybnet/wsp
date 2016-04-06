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
        self._total = {}
        self._completed = {}
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
                new_tasks[t] = self._add_task(t)
        for t in self._tasks.keys():
            if t not in new_tasks:
                self._remove_task(t)
        self._tasks = new_tasks

    """
    添加任务
    """
    def add_task(self, task_id):
        if task_id not in self._tasks:
            self._tasks[task_id] = self._add_task(task_id)

    def record_pulled_request(self, task_id):
        if task_id in self._tasks:
            with self._data_lock:
                self._completed[task_id] += 1

    def record_pushed_request(self, task_id):
        if task_id in self._tasks:
            with self._data_lock:
                self._total[task_id] += 1

    """
    获取上报数据
    """
    async def fetch_data(self):
        await asyncio.sleep(self._report_time)
        data = []
        with self._data_lock:
            for t in self._tasks.keys():
                data.append({"task_id": t,
                             "signature": self._tasks[t],
                             "completed": self._completed[t],
                             "total": self._total[t]})
        return {"task_progress": data}

    def _add_task(self, task_id):
        signature = "%s" % ObjectId()
        self._completed[task_id] = 0
        self._total[task_id] = 0
        return signature

    def _remove_task(self, task_id):
        self._completed.pop(task_id)
        self._total.pop(task_id)
