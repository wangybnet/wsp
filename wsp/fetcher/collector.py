# coding=utf-8

from wsp.config import SystemConfig
from wsp.monitor import MonitorClient
from .config import FetcherConfig
from .collectors import TaskProgressCollector


class CollectorManager:
    """
    管理采集器
    """

    def __init__(self, sys_config, local_config):
        assert isinstance(sys_config, SystemConfig) and isinstance(local_config, FetcherConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._local_config = local_config
        self._monitor_client = MonitorClient(self._sys_config.monitor_addr)
        self._handlers = None
        self._task_progress_collector = TaskProgressCollector(self._local_config)

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

    """
    添加任务
    """
    def add_task(self, task_id):
        self._task_progress_collector.add_task(task_id)

    def record_pulled_request(self, task_id):
        self._task_progress_collector.record_pulled_request(task_id)

    def record_pushed_request(self, task_id):
        self._task_progress_collector.record_pushed_request(task_id)
