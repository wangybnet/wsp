# coding=utf-8

from wsp import downloaderplugins as dplugins
from wsp import spiderplugins as splugins
from wsp.downloader.plugin import DownloaderPluginManager
from wsp.spider.plugin import SpiderPluginManager
from wsp.config import task as tconf


class TaskManager:
    """
    用于管理任务的具体信息
    """

    def __init__(self, sysconf):
        self._sysconf = sysconf
        self._tasks = {}
        self._downloader_plugins = {}
        self._spider_plugins = {}

    """
    改变当前需要管理的任务
    """
    def set_tasks(self, *tasks):
        self._tasks = {}
        self._downloader_plugins = {}
        for task in tasks:
            task_id = "%s" % task.id
            self._tasks[task_id] = task

    """
    根据任务的id获取下载器插件
    """
    def downloader_plugins(self, task_id):
        task_id = "%s" % task_id
        assert task_id in self._tasks, "The task (id=%s) is not under the control" % task_id
        task = self._tasks[task_id]
        if task_id not in self._downloader_plugins:
            plugins = [dplugins.RetryPlugin(task.get_config(tconf.MAX_RETRY)),
                       dplugins.ProxyPlugin(self._sysconf.agent_addr),
                       # dplugins.CheckPlugin(task.get_config(tconf.CHECK)),
                       dplugins.DumpPlugin(self._sysconf.mongo_addr),
                       dplugins.PersistencePlugin(self._sysconf.mongo_addr)]
            self._downloader_plugins[task_id] = DownloaderPluginManager(*plugins)
        return self._downloader_plugins[task_id]

    """
    根据任务的id获取Spider插件
    """
    def spider_plugins(self, task_id):
        task_id = "%s" % task_id
        assert task_id in self._tasks, "The task (id=%s) is not under the control" % task_id
        task = self._tasks[task_id]
        if task_id not in self._spider_plugins:
            plugins = [splugins.LevelLimitPlugin(task.get_config(tconf.MAX_LEVEL)), ]
            self._spider_plugins[task_id] = SpiderPluginManager(*plugins)
        return self._spider_plugins[task_id]
