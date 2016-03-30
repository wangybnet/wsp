# encoding: utf-8

import logging
from xmlrpc.server import SimpleXMLRPCServer

from bson.objectid import ObjectId
from pymongo import MongoClient

from wsp.fetcher.fetcherManager import fetcherManager
from wsp.config.system import SystemConfig
from .task import WspTask
from .config import MasterConfig

log = logging.getLogger(__name__)


class MasterRpcServer(SimpleXMLRPCServer):
    
    def __init__(self, *args, **kw):
        self.client_ip = None
        super(MasterRpcServer, self).__init__(*args, **kw)

    def process_request(self, request, client_address):
        self.client_ip, _ = client_address
        return super(MasterRpcServer, self).process_request(request, client_address)


class Master(object):
    """
    Master类的功能:
        [1].新建任务,任务建立成功返回任务ID
        [2].删除任务,删除成功返回true
        [3].启动单个任务,启动成功返回true
        [4].停止单个任务,停止成功返回true
        [5].返回配置文件信息供fetcher使用
    """

    def __init__(self, master_config, sys_config):
        assert isinstance(master_config, MasterConfig) and isinstance(sys_config, SystemConfig), "Wrong configuration"
        log.debug("New master with addr=%s, config={kafka_addr=%s, mongo_addr=%s}" % (master_config.rpc_addr,
                                                                                      sys_config.kafka_addr,
                                                                                      sys_config.mongo_addr))
        self._master_config = master_config
        self._sys_config = sys_config
        self.fetcher_manager = fetcherManager(self._sys_config)
        self._rpc_server = self._create_rpc_server()
        self._mongo_client = MongoClient(self._sys_config.mongo_addr)

    def _create_rpc_server(self):
        host, port = self._master_config.rpc_addr.split(":")
        port = int(port)
        server = MasterRpcServer((host, port), allow_none=True)
        server.register_function(self.create_one)
        server.register_function(self.delete_one)
        server.register_function(self.start_one)
        server.register_function(self.stop_one)
        server.register_function(self.get_sys_config)
        server.register_function(self.register_fetcher)
        return server

    # 建立mongodb连接并选择集合
    def _get_col(self, db_name, col_name):
        return self._mongo_client[db_name][col_name]

    def create_one(self, task_info, task_config_zip):
        task = WspTask(**task_info)
        task.status = 0
        log.info("Create the task %s with id=%s" % (task.to_dict(), task.id))
        self._get_col(self._sys_config.mongo_db, self._sys_config.mongo_task_tbl).insert_one(task.to_dict())
        # 上传zip
        log.debug("Update zip (_id=%s) to %s.%s" % (task.id,
                                                    self._sys_config.mongo_db,
                                                    self._sys_config.mongo_task_config_tbl))
        self._get_col(self._sys_config.mongo_db, self._sys_config.mongo_task_config_tbl).insert_one(
            {"_id": ObjectId(task.id), self._sys_config.mongo_task_config_zip: task_config_zip.data})
        return task.id

    def delete_one(self, task_id):
        log.info("Delete the task %s" % task_id)
        flag = self.fetcher_manager.delete_one(task_id)
        if not flag:
            return False
        flag = self._get_col(self._sys_config.mongo_db, self._sys_config.mongo_task_tbl).remove({'_id': ObjectId(task_id)})
        return flag

    def start_one(self, task_id):
        log.info("Start the task %s" % task_id)
        flag = self.fetcher_manager.start_one(task_id)
        return flag

    def stop_one(self, task_id):
        log.info("Stop the task %s" % task_id)
        flag = self.fetcher_manager.stop_one(task_id)
        return flag

    def get_sys_config(self):
        log.debug("Return the configuration")
        return self._sys_config

    def register_fetcher(self, port):
        fetcher_addr = "%s:%d" % (self._rpc_server.client_ip, port)
        log.info("The fetcher at %s is registered" % fetcher_addr)
        self.fetcher_manager.add_fetcher(fetcher_addr)
        return fetcher_addr

    def start(self):
        log.info("Start master RPC at %s" % self._master_config.rpc_addr)
        self._rpc_server.serve_forever()
