# coding=utf-8

import logging
import pickle
import time
import re
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from pymongo import MongoClient
from bson.objectid import ObjectId
from kafka import KafkaProducer
from kafka import KafkaConsumer

from wsp.master.config import WspConfig
from wsp.master.task import WspTask
from wsp.downloader import Downloader
from wsp.downloader.http import HttpRequest, HttpResponse
from wsp.fetcher.request import WspRequest
from wsp.utils.fetcher import reconvert_request, reconvert_response, reconvert_error

log = logging.getLogger(__name__)


class Fetcher:
    # FIXME: 根据任务设置spider，plugin
    def __init__(self, master_addr, fetcher_addr, downloader_clients):
        log.debug("New fetcher with master_addr=%s, fetcher_addr=%s, downloader_clients=%d" % (master_addr, fetcher_addr, downloader_clients))
        if not master_addr.startswith("http://"):
            master_addr = "http://" + master_addr
        self.master_addr = master_addr
        self._host, self._port = fetcher_addr.split(":")
        self._port = int(self._port)
        kafka_addr, mongo_addr = self._pull_config_from_master()
        client = MongoClient(mongo_addr)
        self.db = client.wsp
        self.isRunning = False
        self._addr = None
        self.rpcServer = self._create_rpc_server()
        self.producer = KafkaProducer(bootstrap_servers=[kafka_addr, ])
        self.consumer = KafkaConsumer(bootstrap_servers=[kafka_addr, ], auto_offset_reset='earliest')
        self.downloader = Downloader(clients=downloader_clients)
        self.taskDict = {}
        self._task_lock = threading.Lock()

    def _pull_config_from_master(self):
        rpc_client = ServerProxy(self.master_addr, allow_none=True)
        conf = WspConfig(**rpc_client.get_config())
        log.debug("Get the configuration={kafka_addr=%s, mongo_addr=%s, agent_addr=%s}" % (conf.kafka_addr, conf.mongo_addr, conf.agent_addr))
        return conf.kafka_addr, conf.mongo_addr

    def _register(self):
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
        self._register()

    def _start_rpc_server(self):
        log.info("Start RPC server at %s:%d" % (self._host, self._port))
        t = threading.Thread(target=self.rpcServer.serve_forever)
        t.start()

    def changeTasks(self, tasks):
        topics = []
        for t in tasks:
            t = WspTask(**t)
            topic = '%s' % t.id
            topics.append(topic)
        with self._task_lock:
            log.debug("Subscribe topics %s" % topics)
            if topics:
                self.consumer.subscribe(topics)
            self.taskDict = {}
            for t in tasks:
                t = WspTask(**t)
                self.taskDict[t.id] = t

    def pushReq(self, req):
        topic = '%s' % req.task_id
        log.debug("Push WSP request (id=%s, url=%s) into the topic %s" % (req.id, req.url, topic))
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
                log.debug("The WSP request (id=%s, url=%s) has been pulled" % (req.id, req.url))
                self._push_task(req)

    def _start_pull_req(self):
        log.info("Start to pull requests")
        t = threading.Thread(target=self._pull_req)
        t.start()

    def _push_task(self, req):
        while True:
            if self.downloader.add_task(req, self.saveResult):
                break
            # FIXME: 这里暂定休息1s
            sleep_time = 1
            log.debug("Downloader is busy, and I will sleep %s seconds" % sleep_time)
            time.sleep(sleep_time)

    async def saveResult(self, request, result):
        if isinstance(result, HttpRequest):
            req = reconvert_request(result)
            self._push_task()
            self.producer.flush()
        elif isinstance(result, HttpResponse):
            # FIXME: 调用对应的spider
            pass
        else:
            req, err = reconvert_error(request, result)
            # Do Nothing
