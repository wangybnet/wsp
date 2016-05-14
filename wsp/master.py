# coding=utf-8

import time
import logging
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy


from bson.objectid import ObjectId
from pymongo import MongoClient

from .config import SystemConfig, MasterConfig
from .monitor import MonitorServer
from .collectors import TaskProgressCollector

log = logging.getLogger(__name__)


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
        log.debug("New master with addr=%s, config={kafka_addr=%s, mongo_addr=%s}" % (master_config.master_rpc_addr,
                                                                                      sys_config.kafka_addr,
                                                                                      sys_config.mongo_addr))
        self._config = master_config
        self._sys_config = sys_config
        self.fetcher_manager = FetcherManager(self._sys_config)
        self._rpc_server = self._create_rpc_server()
        self._mongo_client = MongoClient(self._sys_config.mongo_addr)
        self._collector_manager = CollectorManager(self._sys_config, self._config)

    def start(self):
        self._start_rpc_server()
        self._collector_manager.open()

    def _start_rpc_server(self):
        log.info("Start master RPC at %s" % self._config.master_rpc_addr)
        t = threading.Thread(target=self._rpc_server.serve_forever)
        t.start()

    # 建立mongodb连接并选择集合
    def _get_col(self, db_name, col_name):
        return self._mongo_client[db_name][col_name]

    def _create_rpc_server(self):
        host, port = self._config.master_rpc_addr.split(":")
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
        server.register_function(self.get_task_progress, "task_progress")
        server.register_function(self.get_running_tasks, "running_tasks")
        return server

    def create_task(self, task_info, task_config_zip):
        task = WspTask(**task_info)
        task.status = WspTask.TASK_CREATE
        if task.create_time is None:
            task.create_time = int(time.time())
        log.info("Create the task %s" % task.to_dict())
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
        log.info("Task %s is finished" % task_id)
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
        if task_info:
            task_info.pop("_id")
        log.debug("Return the information of task %s: %s" % (task_id, task_info))
        return task_info

    def get_task_progress(self, task_id):
        task_progress = self._get_col(self._sys_config.mongo_db, self._sys_config.mongo_task_progress_tbl).find_one({"_id": ObjectId(task_id)})
        if task_progress:
            task_progress.pop("_id")
        log.debug("Return the progress of task %s: %s" % (task_id, task_progress))
        return task_progress

    def get_running_tasks(self):
        running_tasks = self.fetcher_manager.running_tasks
        log.debug("Return the running tasks: %s" % running_tasks)
        return running_tasks


class MasterRpcServer(SimpleXMLRPCServer):

    def __init__(self, *args, **kw):
        self.client_ip = None
        super(MasterRpcServer, self).__init__(*args, **kw)

    def process_request(self, request, client_address):
        self.client_ip, _ = client_address
        return super(MasterRpcServer, self).process_request(request, client_address)


class FetcherManager:

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
            with ServerProxy(fetcher_addr, allow_none=True) as rpc_client:
                rpc_client.change_tasks(self.running_tasks)
        else:
            for f in self.fetcherList:
                with ServerProxy(f, allow_none=True) as rpc_client:
                    rpc_client.change_tasks(self.running_tasks)
        # FIXME: 默认返回True，之后可能根据RPC连接情况修改
        return True

    def _notice_new_task(self, task_id):
        log.debug("Notice the new task %s" % task_id)
        for f in self.fetcherList:
            with ServerProxy(f, allow_none=True) as rpc_client:
                rpc_client.add_task(task_id)
        # FIXME: 默认返回True，之后可能根据RPC连接情况修改
        return True

    def delete_task(self, task_id):
        # TODO: 从Kafka中删除topic
        self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": WspTask.TASK_REMOVED}})
        self.running_tasks.remove(task_id)
        return self._notice_change_tasks()

    def stop_task(self, task_id):
        self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": WspTask.TASK_STOPPED}})
        self.running_tasks.remove(task_id)
        return self._notice_change_tasks()

    def finish_task(self, task_id):
        if task_id in self.running_tasks:
            self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": WspTask.TASK_FINISHED,
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
        if task_id not in self.running_tasks:
            self.running_tasks.append(task_id)
        self.taskTable.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": WspTask.TASK_RUNNING}})
        return self._notice_change_tasks()

    def get_running_tasks(self):
        return self.running_tasks


class CollectorManager:

    def __init__(self, sys_config, local_config):
        assert isinstance(sys_config, SystemConfig) and isinstance(local_config, MasterConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._local_config = local_config
        self._task_progress_collector = TaskProgressCollector(self._sys_config, self._local_config)
        self._monitor_server = MonitorServer(self._local_config.monitor_server_addr,
                                             self._task_progress_collector)

    def open(self):
        self._monitor_server.start()

    def close(self):
        self._monitor_server.stop()


class WspTask:
    TASK_CREATE = 0
    TASK_RUNNING = 1
    TASK_STOPPED = 2
    TASK_FINISHED = 3
    TASK_REMOVED = 4

    def __init__(self, **kw):
        self.id = kw.get("id", "%s" % ObjectId())
        self.create_time = kw.get("create_time", None)
        self.finish_time = kw.get("finish_time", None)
        self.status = kw.get("status", None)
        self.desc = kw.get("desc", None)

    def to_dict(self):
        return {
            '_id': ObjectId(self.id),
            'id': self.id,
            'create_time': self.create_time,
            'finish_time': self.finish_time,
            'status': self.status,
            'desc': self.desc
        }
