# coding=utf-8

import logging
import pickle
import threading
import time
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

from kafka import KafkaConsumer
from kafka import KafkaProducer

from wsp.config import task as tc
from wsp.config import SystemConfig
from wsp.downloader import Downloader
from wsp.http import HttpRequest, HttpResponse
from wsp.spider import Spider
from wsp.utils.parse import pack_request, extract_request, parse_request, unpack_request
from .config import FetcherConfig
from .request import WspRequest
from .taskmanager import TaskManager
from .collector import CollectorManager

log = logging.getLogger(__name__)


class Fetcher:
    # FIXME: 根据任务设置spider
    def __init__(self, config):
        assert isinstance(config, FetcherConfig), "Wrong configuration"
        log.debug("New fetcher with master_rpc_addr=%s, rpc_addr=%s, downloader_clients=%d" % (config.master_rpc_addr, config.rpc_addr, config.downloader_clients))
        self._config = config
        self.master_addr = self._config.master_rpc_addr
        if not self.master_addr.startswith("http://"):
            self.master_addr = "http://%s" % self.master_addr
        self._host, self._port = self._config.rpc_addr.split(":")
        self._port = int(self._port)
        self._sys_config = self._pull_sys_config_from_master()
        self.isRunning = False
        self.rpcServer = self._create_rpc_server()
        self.producer = KafkaProducer(bootstrap_servers=[self._sys_config.kafka_addr, ])
        self.consumer = KafkaConsumer(bootstrap_servers=[self._sys_config.kafka_addr, ],
                                      auto_offset_reset='earliest',
                                      consumer_timeout_ms=self._sys_config.kafka_consumer_timeout_ms)
        self.downloader = Downloader(clients=self._config.downloader_clients)
        self._task_manager = TaskManager(self._sys_config, self._config)
        self._collector_manager = CollectorManager(self._sys_config, self._config)
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
        log.debug("Register on the master at %s" % self.master_addr)
        rpc_client = ServerProxy(self.master_addr, allow_none=True)
        self._addr = rpc_client.register_fetcher(self._port)

    def _create_rpc_server(self):
        server = SimpleXMLRPCServer((self._host, self._port), allow_none=True)
        server.register_function(self.changeTasks)
        server.register_function(self.new_task)
        return server

    def start(self):
        self.isRunning = True
        # open collector manager
        self._collector_manager.open()
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
                self._collector_manager.set_tasks(*tasks)

    """
    通知添加了一个新任务

    主要作用是将起始的URL导入Kafka，在分布式环境下多个Fetch会重复导入起始的URL，这一问题由去重中间件解决。
    """
    def new_task(self, task_id):
        spiders = self._task_manager.spiders(task_id)
        start_urls = self._task_manager.task_config(task_id).get(tc.START_URLS)
        if not isinstance(start_urls, list):
            start_urls = [start_urls]
        for spider in spiders:
            for r in spider.start_requests(start_urls):
                if isinstance(r, HttpRequest):
                    req = WspRequest(task_id=task_id, father_id=task_id, http_request=r)
                    self.pushReq(req)

    def pushReq(self, req):
        topic = '%s' % req.task_id
        log.debug("Push WSP request (id=%s, url=%s) into the topic %s" % (req.id, req.http_request.url, topic))
        # record pushed request
        self._collector_manager.record_pushed_request(req.task_id)
        tempreq = pickle.dumps(req)
        self.producer.send(topic, tempreq)

    def _pull_req(self):
        while self.isRunning:
            with self._task_dict_lock:
                no_work = not self.taskDict
            if no_work:
                sleep_time = self._config.no_work_sleep_time
                log.debug("No work, and I will sleep %s seconds" % sleep_time)
                time.sleep(sleep_time)
            else:
                try:
                    with self._subscribe_lock:
                        record = next(self.consumer)
                    req = pickle.loads(record.value)
                    log.debug("The WSP request (id=%s, url=%s) has been pulled" % (req.id, req.http_request.url))
                    # record pulled request
                    self._collector_manager.record_pulled_request(req.task_id)
                    req.fetcher = self._addr
                    self._push_downloader_task(req)
                except StopIteration as e:
                    log.debug("Kafka read timeout")
                except Exception as e:
                    log.warning("An error occurred when preparing request", exc_info=True)

    def _start_pull_req(self):
        log.info("Start to pull requests")
        t = threading.Thread(target=self._pull_req)
        t.start()

    def _push_downloader_task(self, req):
        request = pack_request(req)
        task_id = "%s" % req.task_id
        while True:
            if self.downloader.add_task(request,
                                        self.saveResult,
                                        middleware=self._task_manager.downloadermws(task_id)):
                break
            sleep_time = self._config.downloader_busy_sleep_time
            log.debug("Downloader is busy, and I will sleep %s seconds" % sleep_time)
            time.sleep(sleep_time)

    async def saveResult(self, request, result):
        req = extract_request(request)
        if isinstance(result, HttpRequest):
            new_req = parse_request(req, result)
            self.pushReq(new_req)
            self.producer.flush()
        elif isinstance(result, HttpResponse):
            # bind HttpRequest
            result.request = request
            task_id = "%s" % req.task_id
            spiders = self._task_manager.spiders(task_id)
            for res in (await Spider.crawl(spiders,
                                           result,
                                           middleware=self._task_manager.spidermws(task_id))):
                if isinstance(res, HttpRequest):
                    new_req = parse_request(req, res)
                    self.pushReq(new_req)
                else:
                    log.debug("Got '%s', but I will do noting here", res)
            self.producer.flush()
        else:
            log.debug("Got an %s error (%s) when request %s, but I will do noting here" % (type(result), result, request.url))
        # NOTE: must unpack here to release the reference of WspRequest in HttpRequest, otherwise will cause GC problem
        unpack_request(request)
