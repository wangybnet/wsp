# coding=utf-8

import logging
import pickle
from xmlrpc.client import ServerProxy

from kafka import KafkaProducer
from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.config.system import SystemConfig
from wsp.master.task import WspTask

log = logging.getLogger(__name__)


class fetcherManager:

    def __init__(self, sys_config):
        assert isinstance(sys_config, SystemConfig), "Wrong configuration"
        log.debug("New fetcher manager with kafka_addr=%s, mongo_addr=%s" % (sys_config.kafka_addr, sys_config.mongo_addr))
        self._sys_config = sys_config
        self.running_tasks = []
        self.fetcherList = []
        self.producer = KafkaProducer(bootstrap_servers=[self._sys_config.kafka_addr, ])
        self._mongo_client = MongoClient(self._sys_config.mongo_addr)
        self.taskTable = self._mongo_client[self._sys_config.mongo_db][self._sys_config.mongo_task_tbl]

    def add_fetcher(self, fetcher_addr):
        if not fetcher_addr.startswith("http://"):
            fetcher_addr = "http://%s" + fetcher_addr
        if fetcher_addr not in self.fetcherList:
            log.debug("Add a new fetcher %s" % fetcher_addr)
            self.fetcherList.append(fetcher_addr)

    def _notice_change_tasks(self):
        log.debug("Change the tasks of the fetchers %s" % self.fetcherList)
        for f in self.fetcherList:
            rpcClient = ServerProxy(f, allow_none=True)
            rpcClient.changeTasks(self.running_tasks)
        # FIXME: 默认返回True，之后可能根据RPC连接情况修改
        return True

    def _notice_new_task(self, task_id):
        log.debug("Change the tasks of the fetchers %s" % self.fetcherList)
        for f in self.fetcherList:
            rpcClient = ServerProxy(f, allow_none=True)
            rpcClient.new_task(task_id)
        # FIXME: 默认返回True，之后可能根据RPC连接情况修改
        return True

    def delete_one(self, task_id):
        # TODO: 从kafka中删除topic
        self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": 3}})
        self.running_tasks.remove(task_id)
        return self._notice_change_tasks()

    def stop_one(self, task_id):
        self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": 2}})
        self.running_tasks.remove(task_id)
        return self._notice_change_tasks()

    def start_one(self, task_id):
        task_dict = self.taskTable.find_one({"_id": ObjectId(task_id)})
        task = WspTask(id=task_id, **task_dict)
        if task.status == 0:
            if not self._notice_new_task(task_id):
                return False
            self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": 1}})
        if task_id not in self.running_tasks:
            self.running_tasks.append(task_id)
        return self._notice_change_tasks()

    def _pushReq(self, req):
        topic = '%s' % req.task_id
        log.debug("Push WSP request (id=%s, url=%s) into the topic %s" % (req.id, req.http_request.url, topic))
        tempreq = pickle.dumps(req)
        self.producer.send(topic, tempreq)
