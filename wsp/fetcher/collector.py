# coding=utf-8

from wsp.config import SystemConfig
from wsp.monitor import MonitorClient
from .collectors import TaskProgressCollector


class CollectorManager:
    """
    管理采集器
    """

    def __init__(self, sys_config):
        assert isinstance(sys_config, SystemConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._monitor_client = MonitorClient(self._sys_config.monitor_addr)
        self._handlers = None
        self._task_progress_collector = TaskProgressCollector(self._sys_config)

    def open(self):
        self._handlers = [self._monitor_client.add_handler(self._task_progress_collector)]

    def close(self):
        self._monitor_client.close()

    """
    设置当前任务

    这里tasks是一个任务ID的列表
    """
    def set_tasks(self, *tasks):
        self._task_progress_collector.set_tasks(*tasks)

    def record_pulled_request(self, task_id):
        self._task_progress_collector.record_pulled_request(task_id)

    def record_pushed_request(self, task_id):
        self._task_progress_collector.record_pushed_request(task_id)
