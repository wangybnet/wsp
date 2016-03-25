# encoding: utf-8

import logging
from xmlrpc.server import SimpleXMLRPCServer

from bson.objectid import ObjectId
from pymongo import MongoClient

from wsp.fetcher.fetcherManager import fetcherManager
from wsp.master.task import WspTask

log = logging.getLogger(__name__)


class MasterRpcServer(SimpleXMLRPCServer):

    def process_request(self, request, client_address):
        self.client_ip, _ = client_address
        return super(MasterRpcServer, self).process_request(request, client_address)


class Master(object):
    '''
    Master类的功能:
        [1].新建任务,任务建立成功返回任务ID
        [2].删除任务,删除成功返回true
        [3].启动单个任务,启动成功返回true
        [4].停止单个任务,停止成功返回true
        [5].返回配置文件信息供fetcher使用
    '''

    def __init__(self, addr, config):
        log.debug("New master with addr=%s, config={kafka_addr=%s, mongo_addr=%s, agent_addr=%s}" % (addr, config.kafka_addr, config.mongo_addr, config.agent_addr))
        self._addr = addr
        self._config = config
        self.fetcher_manager = fetcherManager(self._config.kafka_addr, self._config.mongo_addr)
        self._rpc_server = self._create_rpc_server()
        self._mongo_client = MongoClient(self._config.mongo_addr)

    def _create_rpc_server(self):
        host, port = self._addr.split(":")
        port = int(port)
        server = MasterRpcServer((host, port), allow_none=True)
        server.register_function(self.create_one)
        server.register_function(self.delete_one)
        server.register_function(self.start_one)
        server.register_function(self.stop_one)
        server.register_function(self.get_config)
        server.register_function(self.register_fetcher)
        return server

    # 建立mongodb连接并选择集合
    def __get_col(self, db_name, col_name):
        collection = self._mongo_client[db_name][col_name]
        return collection

    def _find_one(self, obj_id):
         return next(self.__get_col('wsp', 'task').find({'_id': ObjectId(obj_id)}))

    def create_one(self, task):
        if "status" not in task:
            task["status"] = 0
        collection = self.__get_col('wsp', 'task')
        task_id = collection.insert_one(task).inserted_id  # 返回任务ID
        log.info("Create the task %s with id=%s" % (task, task_id))
        return "%s" % task_id

    def delete_one(self, task_id):
        log.info("Delete the task %s" % task_id)
        task = self._find_one(task_id)
        log.debug("The detail of this task: %s" % task)
        task = WspTask(**task, id=task_id)
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.delete(tasks)
        if not flag:
            return False
        flag = self.__get_col('wsp', 'task').remove({'_id': task_id})
        return flag

    def start_one(self, task_id):
        log.info("Start the task %s" % task_id)
        task = self._find_one(task_id)
        log.debug("The detail of this task: %s" % task)
        task = WspTask(**task, id=task_id)
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.start(tasks)
        return flag

    def stop_one(self, task_id):
        log.info("Stop the task %s" % task_id)
        task = self._find_one(task_id)
        log.debug("The detail of this task: %s" % task)
        task = WspTask(**task, id=task_id)
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.stop(tasks)
        return flag

    def get_config(self):
        log.debug("Return the configuration")
        return self._config

    def register_fetcher(self, port):
        fetcher_addr = "%s:%d" % (self._rpc_server.client_ip, port)
        log.info("The fetcher at %s is registered" % fetcher_addr)
        self.fetcher_manager.add_fetcher(fetcher_addr)
        return fetcher_addr

    def start(self):
        log.info("Start master RPC at %s" % self._addr)
        self._rpc_server.serve_forever()
