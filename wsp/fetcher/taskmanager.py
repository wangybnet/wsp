# coding=utf-8

from wsp import downloaderplugins as dplugins


class TaskManager:
    """
    用于管理任务的具体信息
    """
    def __init__(self, wsp_config):
        self._wsp_config = wsp_config
        self._tasks = {}
        self._plugins = {}

    """
    改变当前需要管理的任务
    """
    def set_tasks(self, *tasks):
        self._tasks = {}
        self._plugins = {}
        for task in tasks:
            self._tasks[task.id] = task

    """
    根据任务的id获取下载器插件
    """
    def downloader_plugins(self, task_id):
        assert task_id in self._tasks, "The task (id=%s) is not under the control" % task_id
        task = self._tasks[task_id]
        if task_id not in self._plugins:
            plugins = [dplugins.RetryPlugin(task.max_retry),
                       dplugins.ProxyPlugin(self._wsp_config.agent_addr),
                       dplugins.CheckPlugin(task.check),
                       dplugins.DumpPlugin(self._wsp_config.mongo_addr),
                       dplugins.PersistencePlugin(self._wsp_config.mongo_addr)]
            self._plugins[task_id] = plugins
