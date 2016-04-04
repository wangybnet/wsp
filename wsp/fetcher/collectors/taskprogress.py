# coding=utf-8

import threading

from bson import ObjectId

from wsp.monitor import MonitorClient


class TaskProgressCollector:
    """
    针对每个task有一个handler
    """

    def __init__(self, monitor_client, report_time):
        assert isinstance(monitor_client, MonitorClient), "Wrong configuration"
        self._report_time = report_time
        self._monitor_client = monitor_client
        self._handlers = {}

    """
    改变当前任务

    这里tasks是一个任务ID的列表
    """
    def set_tasks(self, *tasks):
        new_handlers = {}
        for t in tasks:
            if t in self._handlers:
                new_handlers[t] = self._handlers[t]
            else:
                new_handlers[t] = self._load_handler(t)
        for t in self._handlers.keys():
            if t not in new_handlers:
                self._remove_handler(t)
        self._handlers = new_handlers

    """
    添加任务
    """
    def add_task(self, task_id):
        if task_id not in self._handlers:
            self._handlers[task_id] = self._load_handler(task_id)

    def record_pulled_request(self, task_id):
        if task_id in self._handlers:
            self._handlers[task_id].record_pulled_request()

    def record_pushed_request(self, task_id):
        if task_id in self._handlers:
            self._handlers[task_id].record_pushed_request()

    def _load_handler(self, task_id):
        handler = TaskProgressCollector(task_id, self._report_time)
        self._monitor_client.add_handler(handler)
        return handler

    def _remove_handler(self, task_id):
        handler_id = self._handlers[task_id]
        self._monitor_client.remove_handler(handler_id)


class TaskProgressHandler:

    def __init__(self, task_id, report_time):
        self._task_id = task_id
        self._report_time = report_time
        self._id = "%s" % ObjectId()
        self._pulled_count = 0
        self._pushed_count = 0
        self._data_lock = threading.Lock()

    async def fetch_data(self):
        data = {"_key": "task_progress",
                "id": self._id,
                "task_id": self._task_id,
                "pulled_count": self._pulled_count,
                "pushed_count": self._pushed_count}
        return data

    def record_pulled_request(self):
        with self._data_lock:
            self._pulled_count += 1

    def record_pushed_request(self):
        with self._data_lock:
            self._pushed_count += 1
