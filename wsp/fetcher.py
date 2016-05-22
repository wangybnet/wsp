# coding=utf-8

import os
import sys
import time
import pickle
import asyncio
import logging
import zipfile
import threading
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

import yaml
from kafka import KafkaConsumer
from kafka import KafkaProducer
from pymongo import MongoClient
from bson.objectid import ObjectId

from .http import HttpRequest, HttpResponse
from .config import SystemConfig, FetcherConfig, TaskConfig
from .downloader import Downloader, DownloaderMiddlewareManager
from .spider import Spider, SpiderFactory, SpiderMiddlewareManager
from .monitor import MonitorClient
from .reporters import TaskProgressReporter

log = logging.getLogger(__name__)


class Fetcher:

    def __init__(self, config):
        assert isinstance(config, FetcherConfig), "Wrong configuration"
        log.debug("New fetcher with master_rpc_addr=%s, rpc_addr=%s" % (config.master_rpc_addr, config.fetcher_rpc_addr))
        self._config = config
        self.master_addr = self._config.master_rpc_addr
        if not self.master_addr.startswith("http://"):
            self.master_addr = "http://%s" % self.master_addr
        self._host, self._port = self._config.fetcher_rpc_addr.split(":")
        self._port = int(self._port)
        self._sys_config = self._pull_sys_config_from_master()
        self.isRunning = False
        self.rpcServer = self._create_rpc_server()
        self.producer = KafkaProducer(bootstrap_servers=[self._sys_config.kafka_addr, ])
        self.consumer = KafkaConsumer(bootstrap_servers=[self._sys_config.kafka_addr, ],
                                      auto_offset_reset='earliest',
                                      consumer_timeout_ms=self._sys_config.kafka_consumer_timeout_ms)
        self.downloader = Downloader(clients=self._sys_config.downloader_clients, timeout=self._sys_config.downloader_timeout)
        self._task_manager = TaskManager(self._sys_config, self._config)
        self._reporter_manager = ReporterManager(self._sys_config)
        self._request_task = {}
        self.taskDict = {}
        self._subscribe_lock = threading.Lock()
        # NOTE: Fetcher的地址在向Master注册时获取
        self._addr = None

    def _pull_sys_config_from_master(self):
        with ServerProxy(self.master_addr, allow_none=True) as rpc_client:
            conf = SystemConfig(**rpc_client.system_config())
        log.debug("Get the system configuration={kafka_addr=%s, mongo_addr=%s}" % (conf.kafka_addr, conf.mongo_addr))
        return conf

    def _register_on_master(self):
        log.info("Register on the master at %s" % self.master_addr)
        with ServerProxy(self.master_addr, allow_none=True) as rpc_client:
            self._addr = rpc_client.register_fetcher(self._port)

    def _create_rpc_server(self):
        server = SimpleXMLRPCServer((self._host, self._port), allow_none=True)
        server.register_function(self.change_tasks)
        server.register_function(self.add_task)
        return server

    def start(self):
        self.isRunning = True
        self._reporter_manager.open()
        self._start_pull_req()
        self._start_rpc_server()
        self._register_on_master()

    def _start_rpc_server(self):
        log.info("Start RPC server at %s:%d" % (self._host, self._port))
        t = threading.Thread(target=self.rpcServer.serve_forever)
        t.start()

    # NOTE: The tasks here is a list of task IDs.
    def change_tasks(self, tasks):
        topics = [t for t in tasks]
        with self._subscribe_lock:
            log.debug("Subscribe topics %s" % topics)
            if topics:
                self.consumer.subscribe(topics)
            self.taskDict = {}
            for t in tasks:
                self.taskDict[t] = None
            # set current tasks of task manager
            self._task_manager.set_tasks(*tasks)
            # set current tasks of collector managter
            self._reporter_manager.set_tasks(*tasks)

    """
    通知添加了一个新任务

    主要作用是将起始的URL导入Kafka，在分布式环境下多个Fetch会重复导入起始的URL，这一问题由去重中间件解决。
    """
    def add_task(self, task_id):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self._new_task(task_id))

    async def _new_task(self, task_id):
        spiders = self._task_manager.spiders(task_id)
        start_urls = self._task_manager.task_config(task_id).get(TaskConfig.START_URLS, [])
        if not isinstance(start_urls, list):
            start_urls = [start_urls]
        try:
            for res in (await Spider.start_requests(spiders,
                                                    start_urls,
                                                    middleware=self._task_manager.spidermws(task_id))):
                if isinstance(res, HttpRequest):
                    self.push_req(task_id, res)
        except Exception:
            log.warning("Unexpected error occurred when handing start requests", exc_info=True)

    def push_req(self, topic, req):
        log.debug("Push request (url=%s) into the topic %s" % (req.url, topic))
        temp_req = pickle.dumps(req)
        self.producer.send(topic, temp_req)
        task_id = topic
        self._reporter_manager.record_pushed_request(task_id)

    def _pull_req(self):
        sleep_time = self._sys_config.no_work_sleep_time
        while self.isRunning:
            with self._subscribe_lock:
                no_work = not self.taskDict
            if no_work:
                log.debug("No work, and I will sleep %s seconds" % sleep_time)
                time.sleep(sleep_time)
            else:
                try:
                    with self._subscribe_lock:
                        msg = next(self.consumer)
                    req = pickle.loads(msg.value)
                    log.debug("The request (url=%s) has been pulled" % req.url)
                    task_id = msg.topic
                    self._reporter_manager.record_pulled_request(task_id)
                    self._request_task[id(req)] = task_id
                    self._push_downloader_task(task_id, req)
                except StopIteration:
                    log.debug("Kafka read timeout")
                except Exception:
                    log.warning("Unexpected error occurred when pulling request", exc_info=True)

    def _start_pull_req(self):
        log.info("Start to pull requests")
        t = threading.Thread(target=self._pull_req)
        t.start()

    def _push_downloader_task(self, task_id, req):
        self.downloader.add_task(req,
                                 self.save_result,
                                 middleware=self._task_manager.downloadermws(task_id))

    async def save_result(self, request, result):
        req_id = id(request)
        try:
            task_id = self._request_task[req_id]
            if isinstance(result, HttpRequest):
                self.push_req(task_id, result)
                self.producer.flush()
            elif isinstance(result, HttpResponse):
                # bind HttpRequest
                result.request = request
                spiders = self._task_manager.spiders(task_id)
                for res in (await Spider.crawl(spiders,
                                               result,
                                               middleware=self._task_manager.spidermws(task_id))):
                    if isinstance(res, HttpRequest):
                        self.push_req(task_id, res)
                self.producer.flush()
            else:
                log.debug("Got an %s error (%s) when request %s" % (type(result), result, request.url))
        except Exception:
            log.warning("Unexpected error occurred when handing result of downloader", exc_info=True)
        finally:
            if req_id in self._request_task:
                self._request_task.pop(req_id)


class TaskManager:
    """
    用于管理任务的具体信息
    """

    def __init__(self, sys_config, local_config):
        assert isinstance(sys_config, SystemConfig) and isinstance(local_config, FetcherConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._local_config = local_config
        self._mongo_client = MongoClient(self._sys_config.mongo_addr)
        self._task_config_tbl = self._mongo_client[self._sys_config.mongo_db][self._sys_config.mongo_task_config_tbl]
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
    根据任务id获取下载器中间件
    """
    def downloadermws(self, task_id):
        if task_id not in self._tasks:
            self._tasks[task_id] = self._load_task_config(task_id)
        return self._downloadermws[task_id]

    """
    根据任务id获取Spider中间件
    """
    def spidermws(self, task_id):
        if task_id not in self._tasks:
            self._tasks[task_id] = self._load_task_config(task_id)
        return self._spidermws[task_id]

    """
    根据任务id获取Spider
    """
    def spiders(self, task_id):
        if task_id not in self._tasks:
            self._tasks[task_id] = self._load_task_config(task_id)
        return self._spiders[task_id]

    """
    根据任务id获取任务配置
    """
    def task_config(self, task_id):
        if task_id not in self._tasks:
            self._tasks[task_id] = self._load_task_config(task_id)
        return self._tasks[task_id]

    """
    根据任务id加载任务配置
    """
    def _load_task_config(self, task_id):
        code_dir = self._get_code_dir(task_id)
        self._unzip_task(task_id, code_dir)
        config_yaml = "%s/%s" % (code_dir, self._sys_config.task_config_file)
        with open(config_yaml, "r", encoding="utf-8") as f:
            task_config = TaskConfig(**yaml.load(f))
            task_config[TaskConfig.TASK_ID] = task_id
        log.debug("Loaded the configuration of the task %s" % task_id)
        self._load_custom_objects(task_id, task_config, code_dir)
        return task_config

    """
    根据任务id加载任务配置
    """
    def _remove_task_config(self, task_id):
        self._spiders.pop(task_id)
        self._downloadermws.pop(task_id)
        self._spidermws.pop(task_id)

    def _load_custom_objects(self, task_id, task_config, code_dir):
        # 添加sys.path
        sys.path.append(code_dir)
        # 备份sys.modules
        modules_backup = dict(sys.modules)
        self._spiders[task_id] = self._load_spiders(task_config)
        self._downloadermws[task_id] = self._load_downloadermws(task_config)
        self._spidermws[task_id] = self._load_spidermws(task_config)
        # 恢复sys.modules
        sys.modules = modules_backup
        # 移除sys.path
        sys.path.remove(code_dir)

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

    def _unzip_task(self, task_id, code_dir):
        log.debug("Unzip the code of the task %s at '%s'" % (task_id, code_dir))
        zip_json = self._task_config_tbl.find_one({"_id": ObjectId(task_id)})
        zipb = zip_json["zip"]
        if not os.path.exists(code_dir):
            os.makedirs(code_dir, mode=0o775)
        zipf = "%s/%s.zip" % (code_dir, task_id)
        with open(zipf, "wb") as f:
            f.write(zipb)
        with zipfile.ZipFile(zipf, "r") as fz:
            for file in fz.namelist():
                fz.extract(file, code_dir)

    def _get_code_dir(self, task_id):
        return "%s/%s" % (self._local_config.task_code_dir, task_id)


class ReporterManager:

    def __init__(self, sys_config):
        assert isinstance(sys_config, SystemConfig), "Wrong configuration"
        self._sys_config = sys_config
        self._task_progress_reporter = TaskProgressReporter(self._sys_config)
        self._monitor_client = MonitorClient(self._sys_config.monitor_server_addr,
                                             self._task_progress_reporter)

    def open(self):
        self._monitor_client.start()

    def close(self):
        self._monitor_client.stop()

    """
    设置当前任务

    这里tasks是一个任务ID的列表
    """
    def set_tasks(self, *tasks):
        self._task_progress_reporter.set_tasks(*tasks)

    def record_pulled_request(self, task_id):
        self._task_progress_reporter.record_pulled_request(task_id)

    def record_pushed_request(self, task_id):
        self._task_progress_reporter.record_pushed_request(task_id)
