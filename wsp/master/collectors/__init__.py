# coding=utf-8

from wsp.config import SystemConfig
from wsp.monitor import MonitorServer
from ..config import MasterConfig
from .taskprogress import TaskProgressCollector


class CollectorManager:

    def __init__(self, sys_config, local_config):
        assert isinstance(sys_config, SystemConfig) and isinstance(local_config, MasterConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._local_config = local_config
        self._task_progress_collector = TaskProgressCollector(self._sys_config, self._local_config)
        self._monitor_server = MonitorServer(self._local_config.monitor_addr,
                                             self._task_progress_collector)

    def open(self):
        self._monitor_server.start()

    def close(self):
        self._monitor_server.stop()
