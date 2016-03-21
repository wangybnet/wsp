# encoding: utf-8

import logging

from xmlrpc.server import SimpleXMLRPCServer
from pymongo import MongoClient
from wsp.fetcher.fetcherManager import fetcherManager
from wsp.master.task import WspTask


class MasterRpcServer(SimpleXMLRPCServer):

    def process_request(self, request, client_address):
        self.client_addr = client_address
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
        logging.debug("New master with addr=%s, config={kafka_addr=%s, mongo_addr=%s, agent_addr=%s}" % (addr, config.kafka_addr, config.mongo_addr, config.agent_addr))
        self._addr = addr
        self._config = config
        self.fetcher_manager = fetcherManager(self._config.kafka_addr, self._config.mongo_addr)
        self._rpc_server = self._create_rpc_server()
        self._mongo_client = MongoClient(self._config.mongo_addr)

    def _create_rpc_server(self):
        host, port = self._addr.split(":")
        port = int(port)
        server = SimpleXMLRPCServer((host, port), allow_none=True)
        server.register_function(self.create_one)
        server.register_function(self.delete_one)
        server.register_function(self.start_one)
        server.register_function(self.stop_one)
        server.register_function(self.get_config)
        server.register_function(self.register_fetcher)
        return server

    # 建立mongodb连接并选择集合
    def __get_col(self, db_name, col_name):
        addr = self._config.mongo_addr
        collection = self._mongo_client[db_name][col_name]
        return collection

    def create_one(self, task):
        logging.debug("Create the task %s" % task)
        collection = self.__get_col('wsp', 'task')
        task_id = collection.insert_one(task).inserted_id  # 返回任务ID
        logging.info("Create the task %s" % task_id)
        return task_id

    def delete_one(self, task_id):
        logging.info("Delete the task %s" % task_id)
        collection = self.__get_col('wsp', 'task')
        task = collection.find_one({'_id': task_id})
        task = WspTask(**task, id=task_id)
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.delete(tasks)
        if not flag:
            return False
        flag = collection.remove({'_id': task_id})
        return flag

    def start_one(self, task_id):
        logging.info("Start the task %s" % task_id)
        collection = self.__get_col('wsp', 'task')
        task = collection.find_one({'_id': task_id})
        task = WspTask(**task, id=task_id)
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.start(tasks)
        return flag

    def stop_one(self, task_id):
        logging.info("Stop the task %s" % task_id)
        collection = self.__get_col('wsp', 'task')
        task = collection.find_one({'_id': task_id})
        task = WspTask(**task, id=task_id)
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.stop(tasks)
        return flag

    def get_config(self):
        logging.debug("Return the configuration")
        return self._config

    def register_fetcher(self):
        fetcher_addr = self._rpc_server.client_addr
        logging.info("The fetcher at %s is registered" % fetcher_addr)
        self.fetcher_manager.add_fetcher(fetcher_addr)

    def start(self):
        logging.info("Start master RPC at %s" % self._addr)
        self._rpc_server.serve_forever()
