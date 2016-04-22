# coding=utf-8


from wsp.config import SystemConfig
from wsp.monitor import MonitorClient
from .taskprogress import TaskProgressReporter


class ReporterManager:

    def __init__(self, sys_config):
        assert isinstance(sys_config, SystemConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._task_progress_reporter = TaskProgressReporter(self._sys_config)
        self._monitor_client = MonitorClient(self._sys_config.monitor_addr,
                                             self._task_progress_reporter)

    def open(self):
        self._monitor_client.start()

    def close(self):
        self._monitor_client.stop()

    """
    设置当前任务

    这里tasks是一个任务ID的列表
    """
    def set_tasks(self, *tasks):
        self._task_progress_reporter.set_tasks(*tasks)

    def record_pulled_request(self, task_id):
        self._task_progress_reporter.record_pulled_request(task_id)

    def record_pushed_request(self, task_id):
        self._task_progress_reporter.record_pushed_request(task_id)
