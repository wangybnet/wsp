# coding=utf-8

from wsp.config import SystemConfig
from wsp.monitor import MonitorServer
from .config import MasterConfig
from .monitors import TaskProgressMonitor


class MonitorManager:
    """
    管理监视器
    """

    def __init__(self, sys_config, local_config):
        assert isinstance(sys_config, SystemConfig) and isinstance(local_config, MasterConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._local_config = local_config
        self._monitor_server = MonitorServer(self._local_config.monitor_addr)
        self._handlers = None
        self._task_progress_monitor = TaskProgressMonitor(self._sys_config, self._local_config)

    def open(self):
        self._handlers = [self._monitor_server.add_handler(self._task_progress_monitor)]

    def close(self):
        self._monitor_server.stop()
