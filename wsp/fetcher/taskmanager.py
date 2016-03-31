# coding=utf-8

import os
import sys
import zipfile
import logging

from pymongo import MongoClient
from bson.objectid import ObjectId
import yaml

from wsp.downloader.middleware import DownloaderMiddlewareManager
from wsp.spider.middleware import SpiderMiddlewareManager
from wsp.config.task import TaskConfig
from wsp.config.system import SystemConfig
from .config import FetcherConfig
from wsp.spider import SpiderFactory

log = logging.getLogger(__name__)


class TaskManager:
    """
    用于管理任务的具体信息
    """

    def __init__(self, sys_conf, local_conf):
        assert isinstance(sys_conf, SystemConfig) and isinstance(local_conf, FetcherConfig), "Wrong configuration"
        self._sys_conf = sys_conf
        self._local_conf = local_conf
        self._mongo_client = MongoClient(self._sys_conf.mongo_addr)
        # NOTE: tasks里面存在的是<task id, task configuration>的键值对
        self._tasks = {}
        self._downloadermws = {}
        self._spidermws = {}
        self._spiders = {}

    """
    改变当前需要管理的任务

    这里tasks是一个任务ID的列表
    """
    def set_tasks(self, *tasks):
        new_tasks = {}
        for t in tasks:
            if t in self._tasks:
                new_tasks[t] = self._tasks[t]
            else:
                new_tasks[t] = self._load_task_config(t)
        for t in self._tasks.keys():
            if t not in new_tasks:
                self._remove_task_config(t)
        self._tasks = new_tasks

    """
    添加一个需要管理的任务
    """
    def add_task(self, task_id):
        self._tasks[task_id] = self._load_task_config(task_id)

    """
    根据任务id获取下载器中间件
    """
    def downloadermws(self, task_id):
        assert task_id in self._tasks, "The task (id=%s) is not under the control" % task_id
        return self._downloadermws[task_id]

    """
    根据任务id获取Spider中间件
    """
    def spidermws(self, task_id):
        assert task_id in self._tasks, "The task (id=%s) is not under the control" % task_id
        return self._spidermws[task_id]

    """
    根据任务id获取Spider
    """
    def spiders(self, task_id):
        assert task_id in self._tasks, "The task (id=%s) is not under the control" % task_id
        return self._spiders[task_id]

    """
    根据任务id获取任务配置
    """
    def task_config(self, task_id):
        assert task_id in self._tasks, "The task (id=%s) is not under the control" % task_id
        return self._tasks[task_id]

    """
    根据任务id加载任务配置
    """
    def _load_task_config(self, task_id):
        code_dir = self._get_code_dir(task_id)
        self._install_task(task_id, code_dir)
        config_yaml = "%s/%s" % (code_dir, self._sys_conf.task_config_file)
        with open(config_yaml, "r", encoding="utf-8") as f:
            task_config = TaskConfig(**yaml.load(f))
        log.debug("Loaded the configuration of the task %s" % task_id)
        # 添加sys.path
        sys.path.append(code_dir)
        self._spiders[task_id] = self._load_spiders(task_config)
        self._downloadermws[task_id] = self._load_downloadermws(task_config)
        self._spidermws[task_id] = self._load_spidermws(task_config)
        # 移除sys.path
        sys.path.remove(code_dir)
        return task_config

    """
    根据任务id加载任务配置
    """
    def _remove_task_config(self, task_id):
        self._spiders.pop(task_id)
        self._downloadermws.pop(task_id)
        self._spidermws.pop(task_id)

    """
    根据任务配置加载下载器中间件
    """
    @staticmethod
    def _load_downloadermws(task_config):
        return DownloaderMiddlewareManager.from_config(task_config)

    """
    根据任务配置加载Spider中间件
    """
    @staticmethod
    def _load_spidermws(task_config):
        return SpiderMiddlewareManager.from_config(task_config)

    """
    根据任务配置加载Spider
    """
    @staticmethod
    def _load_spiders(task_config):
        return SpiderFactory.create(task_config)

    def _install_task(self, task_id, code_dir):
        log.debug("Install task %s at '%s'" % (task_id, code_dir))
        zip_json = self._mongo_client[self._sys_conf.mongo_db][self._sys_conf.mongo_task_config_tbl].find_one({"_id": ObjectId(task_id)})
        zipb = zip_json[self._sys_conf.mongo_task_config_zip]
        if not os.path.exists(code_dir):
            os.makedirs(code_dir, mode=0o775)
        zipf = "%s/%s.zip" % (code_dir, task_id)
        with open(zipf, "wb") as f:
            f.write(zipb)
        with zipfile.ZipFile(zipf, "r") as fz:
            for file in fz.namelist():
                fz.extract(file, code_dir)

    def _get_code_dir(self, task_id):
        return "%s/%s" % (self._local_conf.task_code_dir, task_id)
