# coding=utf-8

import logging
import pickle
import threading
import time
import asyncio
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

from kafka import KafkaConsumer
from kafka import KafkaProducer

from wsp.config import task as tc
from wsp.config import SystemConfig
from wsp.downloader import Downloader
from wsp.http import HttpRequest, HttpResponse
from wsp.spider import Spider
from .config import FetcherConfig
from .taskmanager import TaskManager
from .reportermanager import ReporterManager

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
        self._task_dict_lock = threading.Lock()
        self._subscribe_lock = threading.Lock()
        # NOTE: Fetcher的地址在向Master注册时获取
        self._addr = None

    def _pull_sys_config_from_master(self):
        rpc_client = ServerProxy(self.master_addr, allow_none=True)
        conf = SystemConfig(**rpc_client.system_config())
        log.debug("Get the system configuration={kafka_addr=%s, mongo_addr=%s}" % (conf.kafka_addr, conf.mongo_addr))
        return conf

    def _register_on_master(self):
        log.info("Register on the master at %s" % self.master_addr)
        rpc_client = ServerProxy(self.master_addr, allow_none=True)
        self._addr = rpc_client.register_fetcher(self._port)

    def _create_rpc_server(self):
        server = SimpleXMLRPCServer((self._host, self._port), allow_none=True)
        server.register_function(self.changeTasks)
        server.register_function(self.new_task)
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
    def changeTasks(self, tasks):
        topics = [t for t in tasks]
        with self._task_dict_lock:
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
    def new_task(self, task_id):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self._new_task(task_id))

    async def _new_task(self, task_id):
        spiders = self._task_manager.spiders(task_id)
        start_urls = self._task_manager.task_config(task_id).get(tc.START_URLS, [])
        if not isinstance(start_urls, list):
            start_urls = [start_urls]
        try:
            for res in (await Spider.start_requests(spiders,
                                                    start_urls,
                                                    middleware=self._task_manager.spidermws(task_id))):
                if isinstance(res, HttpRequest):
                    self.pushReq(task_id, res)
        except Exception:
            log.warning("Unexpected error occurred when handing start requests", exc_info=True)

    def pushReq(self, topic, req):
        log.debug("Push request (url=%s) into the topic %s" % (req.url, topic))
        temp_req = pickle.dumps(req)
        self.producer.send(topic, temp_req)
        task_id = topic
        self._reporter_manager.record_pushed_request(task_id)

    def _pull_req(self):
        while self.isRunning:
            with self._task_dict_lock:
                no_work = not self.taskDict
            if no_work:
                sleep_time = self._sys_config.no_work_sleep_time
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
                                 self.saveResult,
                                 middleware=self._task_manager.downloadermws(task_id))

    async def saveResult(self, request, result):
        req_id = id(request)
        try:
            task_id = self._request_task[req_id]
            if isinstance(result, HttpRequest):
                self.pushReq(task_id, result)
                self.producer.flush()
            elif isinstance(result, HttpResponse):
                # bind HttpRequest
                result.request = request
                spiders = self._task_manager.spiders(task_id)
                for res in (await Spider.crawl(spiders,
                                               result,
                                               middleware=self._task_manager.spidermws(task_id))):
                    if isinstance(res, HttpRequest):
                        self.pushReq(task_id, res)
                self.producer.flush()
            else:
                log.debug("Got an %s error (%s) when request %s" % (type(result), result, request.url))
        except Exception:
            log.warning("Unexpected error occurred when handing result of downloader", exc_info=True)
        finally:
            if req_id in self._request_task:
                self._request_task.pop(req_id)
