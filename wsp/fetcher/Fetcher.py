# coding=utf-8

import logging
import pickle
import time
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from pymongo import MongoClient
from kafka import KafkaProducer
from kafka import KafkaConsumer

from wsp.master.config import WspConfig
from wsp.config.task import WspTask
from wsp.downloader import Downloader
from wsp.downloader.http import HttpRequest, HttpResponse
from wsp.utils.fetcher import pack_request, unpack_request, parse_request
from .taskmanager import TaskManager

log = logging.getLogger(__name__)


class Fetcher:
    # FIXME: 根据任务设置spider
    def __init__(self, master_addr, fetcher_addr, downloader_clients):
        log.debug("New fetcher with master_addr=%s, fetcher_addr=%s, downloader_clients=%d" % (master_addr, fetcher_addr, downloader_clients))
        if not master_addr.startswith("http://"):
            master_addr = "http://" + master_addr
        self.master_addr = master_addr
        self._host, self._port = fetcher_addr.split(":")
        self._port = int(self._port)
        self._wsp_config = self._pull_config_from_master()
        client = MongoClient(self._wsp_config.mongo_addr)
        self.db = client.wsp
        self.isRunning = False
        self._addr = None
        self.rpcServer = self._create_rpc_server()
        self.producer = KafkaProducer(bootstrap_servers=[self._wsp_config.kafka_addr, ])
        self.consumer = KafkaConsumer(bootstrap_servers=[self._wsp_config.kafka_addr, ], auto_offset_reset='earliest')
        self.downloader = Downloader(clients=downloader_clients)
        self._task_manager = TaskManager(self._wsp_config)
        self.taskDict = {}
        self._task_lock = threading.Lock()

    def _pull_config_from_master(self):
        rpc_client = ServerProxy(self.master_addr, allow_none=True)
        conf = WspConfig(**rpc_client.get_config())
        log.debug("Get the configuration={kafka_addr=%s, mongo_addr=%s, agent_addr=%s}" % (conf.kafka_addr, conf.mongo_addr, conf.agent_addr))
        return conf

    def _register_on_master(self):
        log.debug("Register on the master at %s" % self.master_addr)
        rpc_client = ServerProxy(self.master_addr, allow_none=True)
        self._addr = rpc_client.register_fetcher(self._port)

    def _create_rpc_server(self):
        server = SimpleXMLRPCServer((self._host, self._port), allow_none=True)
        server.register_function(self.changeTasks)
        return server

    def start(self):
        self.isRunning = True
        self._start_pull_req()
        self._start_rpc_server()
        self._register_on_master()

    def _start_rpc_server(self):
        log.info("Start RPC server at %s:%d" % (self._host, self._port))
        t = threading.Thread(target=self.rpcServer.serve_forever)
        t.start()

    def changeTasks(self, tasks):
        wsp_tasks = [WspTask(**t) for t in tasks]
        topics = []
        for t in wsp_tasks:
            topic = '%s' % t.id
            topics.append(topic)
        with self._task_lock:
            log.debug("Subscribe topics %s" % topics)
            if topics:
                self.consumer.subscribe(topics)
            self.taskDict = {}
            for t in wsp_tasks:
                self.taskDict[t.id] = t
            # set current tasks of task manager
            self._task_manager.set_tasks(*wsp_tasks)

    def pushReq(self, req):
        topic = '%s' % req.task_id
        log.debug("Push WSP request (id=%s, url=%s) into the topic %s" % (req.id, req.http_request.url, topic))
        tempreq = pickle.dumps(req)
        self.producer.send(topic, tempreq)

    def _pull_req(self):
        while self.isRunning:
            with self._task_lock:
                no_work = not self.taskDict
            if no_work:
                # FIXME: 这里暂定休息5s
                sleep_time = 5
                log.debug("No work, and I will sleep %s seconds" % sleep_time)
                time.sleep(sleep_time)
            else:
                record = next(self.consumer)
                req = pickle.loads(record.value)
                log.debug("The WSP request (id=%s, url=%s) has been pulled" % (req.id, req.http_request.url))
                # 添加处理该请求的fetcher的地址
                req.fetcher = self._addr
                self._push_task(req)

    def _start_pull_req(self):
        log.info("Start to pull requests")
        t = threading.Thread(target=self._pull_req)
        t.start()

    def _push_task(self, req):
        request = pack_request(req)
        task_id = "%s" % req.task_id
        while True:
            if self.downloader.add_task(request, self.saveResult, plugin=self._task_manager.downloader_plugins(task_id)):
                break
            # FIXME: 这里暂定休息1s
            sleep_time = 1
            log.debug("Downloader is busy, and I will sleep %s seconds" % sleep_time)
            time.sleep(sleep_time)

    async def saveResult(self, request, result):
        # NOTE: must unpack here to release the reference of WspRequest in HttpRequest, otherwise will cause GC problem
        req = unpack_request(request)
        if isinstance(result, HttpRequest):
            res = parse_request(req, result)
            self.pushReq(req)
            self.producer.flush()
        elif isinstance(result, HttpResponse):
            # FIXME: 调用对应的spider
            log.debug("I will use spider to handle the response soon")
        else:
            log.debug("Got an error (%s) when request %s, but I will do noting here" % (result, request.url))
            raise result
