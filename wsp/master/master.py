# encoding: utf-8

import logging
import threading
from xmlrpc.server import SimpleXMLRPCServer

from bson.objectid import ObjectId
from pymongo import MongoClient

from wsp.config import SystemConfig
from .fetcherManager import fetcherManager
from .config import MasterConfig
from .task import WspTask
from .task import TASK_CREATE
from .monitor import MonitorManager

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
        self._config = master_config
        self._sys_config = sys_config
        self.fetcher_manager = fetcherManager(self._sys_config)
        self._rpc_server = self._create_rpc_server()
        self._mongo_client = MongoClient(self._sys_config.mongo_addr)
        self._monitor_manager = MonitorManager(self._sys_config, self._config)

    def start(self):
        self._start_rpc_server()
        # open monitor manager
        self._monitor_manager.open()

    def _start_rpc_server(self):
        log.info("Start master RPC at %s" % self._config.rpc_addr)
        t = threading.Thread(target=self._rpc_server.serve_forever)
        t.start()

    # 建立mongodb连接并选择集合
    def _get_col(self, db_name, col_name):
        return self._mongo_client[db_name][col_name]

    def _create_rpc_server(self):
        host, port = self._config.rpc_addr.split(":")
        port = int(port)
        server = MasterRpcServer((host, port), allow_none=True)
        server.register_function(self.create_task)
        server.register_function(self.delete_task)
        server.register_function(self.start_task)
        server.register_function(self.stop_task)
        server.register_function(self.finish_task)
        server.register_function(self.get_system_config, "system_config")
        server.register_function(self.register_fetcher)
        server.register_function(self.get_task_info, "task_info")
        server.register_function(self.get_running_tasks, "running_tasks")
        return server

    def create_task(self, task_info, task_config_zip):
        task = WspTask(**task_info)
        task.status = TASK_CREATE
        log.info("Create the task %s with id=%s" % (task.to_dict(), task.id))
        self._get_col(self._sys_config.mongo_db, self._sys_config.mongo_task_tbl).insert_one(task.to_dict())
        # 上传zip
        log.debug("Upload zip (_id=%s) to collection '%s.%s'" % (task.id,
                                                                 self._sys_config.mongo_db,
                                                                 self._sys_config.mongo_task_config_tbl))
        self._get_col(self._sys_config.mongo_db, self._sys_config.mongo_task_config_tbl).insert_one(
            {"_id": ObjectId(task.id), "zip": task_config_zip.data})
        return task.id

    def delete_task(self, task_id):
        log.info("Delete the task %s" % task_id)
        flag = self.fetcher_manager.delete_task(task_id)
        return flag

    def start_task(self, task_id):
        log.info("Start the task %s" % task_id)
        flag = self.fetcher_manager.start_task(task_id)
        return flag

    def stop_task(self, task_id):
        log.info("Stop the task %s" % task_id)
        flag = self.fetcher_manager.stop_task(task_id)
        return flag

    def finish_task(self, task_id):
        log.info("Task %s is finished %s" % task_id)
        flag = self.fetcher_manager.finish_task(task_id)
        return flag

    def get_system_config(self):
        log.debug("Return the system configuration")
        return self._sys_config

    def register_fetcher(self, port):
        fetcher_addr = "%s:%d" % (self._rpc_server.client_ip, port)
        log.info("The fetcher at %s is registered" % fetcher_addr)
        self.fetcher_manager.add_fetcher(fetcher_addr)
        return fetcher_addr

    def get_task_info(self, task_id):
        task_info = self._get_col(self._sys_config.mongo_db, self._sys_config.mongo_task_tbl).find_one({"_id": ObjectId(task_id)})
        log.debug("Return the status of task %s: %s" % (task_id, task_info))
        return task_info

    def get_running_tasks(self, task_id):
        running_tasks = self.fetcher_manager.running_tasks
        log.debug("Return the running tasks: %s" % running_tasks)
        return running_tasks

    def get_task_progress(self, task_id):
        task_progress = self._get_col(self._sys_config.mongo_db, self._sys_config.mongo_task_progress_tbl).find_one({"_id": ObjectId(task_id)})
        log.debug("Return the status of task %s: %s" % (task_id, task_progress))
        return task_progress
