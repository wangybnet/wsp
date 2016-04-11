# coding=utf-8

import logging
from xmlrpc.client import ServerProxy
import time

from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.config import SystemConfig
from wsp.master.task import WspTask
from wsp.master.task import TASK_RUNNING, TASK_STOPPED, TASK_REMOVED, TASK_FINISHED

log = logging.getLogger(__name__)


class fetcherManager:

    def __init__(self, sys_config):
        assert isinstance(sys_config, SystemConfig), "Wrong configuration"
        log.debug("New fetcher manager with kafka_addr=%s, mongo_addr=%s" % (sys_config.kafka_addr, sys_config.mongo_addr))
        self._sys_config = sys_config
        self.running_tasks = []
        self.fetcherList = []
        self._mongo_client = MongoClient(self._sys_config.mongo_addr)
        self.taskTable = self._mongo_client[self._sys_config.mongo_db][self._sys_config.mongo_task_tbl]

    def add_fetcher(self, fetcher_addr):
        if not fetcher_addr.startswith("http://"):
            fetcher_addr = "http://%s" % fetcher_addr
        if fetcher_addr not in self.fetcherList:
            log.debug("Add a new fetcher %s" % fetcher_addr)
            self.fetcherList.append(fetcher_addr)
            self._notice_change_tasks(fetcher_addr)

    def _notice_change_tasks(self, fetcher_addr=None):
        log.debug("Notice %s to change the tasks" % (fetcher_addr if fetcher_addr else "all the fetchers"))
        if fetcher_addr:
            rpcClient = ServerProxy(fetcher_addr, allow_none=True)
            rpcClient.changeTasks(self.running_tasks)
        else:
            for f in self.fetcherList:
                rpcClient = ServerProxy(f, allow_none=True)
                rpcClient.changeTasks(self.running_tasks)
        # FIXME: 默认返回True，之后可能根据RPC连接情况修改
        return True

    def _notice_new_task(self, task_id):
        log.debug("Notice the new task %s" % task_id)
        for f in self.fetcherList:
            rpcClient = ServerProxy(f, allow_none=True)
            rpcClient.new_task(task_id)
        # FIXME: 默认返回True，之后可能根据RPC连接情况修改
        return True

    def delete_task(self, task_id):
        # TODO: 从Kafka中删除topic
        self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": TASK_REMOVED}})
        self.running_tasks.remove(task_id)
        return self._notice_change_tasks()

    def stop_task(self, task_id):
        self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": TASK_STOPPED}})
        self.running_tasks.remove(task_id)
        return self._notice_change_tasks()

    def finish_task(self, task_id):
        if task_id in self.running_tasks:
            self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": TASK_FINISHED,
                                                                            "finish_time": int(time.time())}})
            self.running_tasks.remove(task_id)
            return self._notice_change_tasks()
        return False

    def start_task(self, task_id):
        task_dict = self.taskTable.find_one({"_id": ObjectId(task_id)})
        task = WspTask(**task_dict)
        if task.status == 0:
            if not self._notice_new_task(task_id):
                return False
            self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": TASK_RUNNING}})
        if task_id not in self.running_tasks:
            self.running_tasks.append(task_id)
        return self._notice_change_tasks()

    def get_running_tasks(self):
        return self.running_tasks
