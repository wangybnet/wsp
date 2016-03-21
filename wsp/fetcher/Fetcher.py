# coding=utf-8

import logging
import pickle
import time
import re
import socket
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from pymongo import MongoClient
from bson.objectid import ObjectId
from kafka import KafkaProducer
from kafka import KafkaConsumer
from aiohttp.client_reqrep import helpers

from wsp.master.config import WspConfig
from wsp.master.task import WspTask
from wsp.downloader import Downloader
from wsp.downloader.http import HttpRequest, HttpError
from wsp.fetcher.request import WspRequest
from wsp.fetcher.response import WspResponse


# 将WSP的request转换成Downloader的request
def _convert_request(func):
    def wrapper(req):
        request = HttpRequest(req.url, proxy=req.proxy, headers=req.headers)
        request._wspreq = req
        return func(request)

    return wrapper


# 将Downloader的request和reponse转换成WSP的request和response
def _convert_result(func):
    def wrapper(req, resp):
        request = req._wspreq
        # FIXME: 这种获取本机IP地址的方式在Linux下面可能获取到类似127.*.*.*的地址
        request.fetcher = socket.gethostbyname(socket.gethostname())
        response = WspResponse(req_id=request.id,
                               task_id=request.task_id,
                               url=request.url)
        if isinstance(resp, HttpError):
            response.error = "%s" % resp.error
        else:
            if resp.body is not None:
                ctype = resp.headers.get("Content-Type", "").lower()
                mtype, _, _, params = helpers.parse_mimetype(ctype)
                if mtype == "text":
                    encoding = params.get("charset")
                    # if not encoding:
                    #     encoding = chardet.detect(resp.body)["encoding"]
                    if not encoding:
                        encoding = "utf-8"
                    response.html = resp.body.decode(encoding)
            response.url = request.url
            response.http_code = resp.status
            response.headers = resp.headers
            response.body = resp.body
        return func(request, response)

    return wrapper


class Fetcher:
    def __init__(self, master_addr, fetcher_addr, downloader_clients):
        logging.debug("New fetcher with master_addr=%s, fetcher_addr=%s, downloader_clients=%d" % (master_addr, fetcher_addr, downloader_clients))
        if not master_addr.startswith("http://"):
            master_addr = "http://" + master_addr
        self.master_addr = master_addr
        self._host, self._port = fetcher_addr.split(":")
        self._port = int(self._port)
        kafka_addr, mongo_addr = self._pull_config_from_master()
        client = MongoClient(mongo_addr)
        self.db = client.wsp
        self.isRunning = True
        self.rpcServer = self._create_rpc_server()
        self.producer = KafkaProducer(bootstrap_servers=[kafka_addr, ])
        self.consumer = KafkaConsumer(bootstrap_servers=[kafka_addr, ], auto_offset_reset='earliest')
        self.downloader = Downloader(clients=downloader_clients)
        self.taskDict = {}
        self._task_lock = threading.Lock()

    def _pull_config_from_master(self):
        rpc_client = ServerProxy(self.master_addr, allow_none=True)
        conf = WspConfig(**rpc_client.get_config())
        logging.debug("Get the configuration={kafka_addr=%s, mongo_addr=%s, agent_addr=%s}" % (conf.kafka_addr, conf.mongo_addr, conf.agent_addr))
        return conf.kafka_addr, conf.mongo_addr

    def _register(self):
        logging.debug("Register on the master at %s" % self.master_addr)
        rpc_client = ServerProxy(self.master_addr, allow_none=True)
        rpc_client.register_fetcher(self._port)

    def _create_rpc_server(self):
        server = SimpleXMLRPCServer((self._host, self._port), allow_none=True)
        server.register_function(self.changeTasks)
        return server

    def start(self):
        self._start_pull_req()
        self._start_rpc_server()
        self._register()

    def _start_rpc_server(self):
        logging.info("Start RPC server at %s:%d" % (self._addr, self._port))
        t = threading.Thread(target=self.rpcServer.serve_forever)
        t.start()

    def changeTasks(self, tasks):
        topics = []
        for t in tasks:
            t = WspTask(**t)
            topic = '%d' % t.id
            topics.append(topic)
        with self._task_lock:
            logging.debug("Subscribe topics %s" % topics)
            self.consumer.subscribe(topics)
            self.taskDict = {}
            for t in tasks:
                self.taskDict[t.id] = t

    def pushReq(self, req):
        topic = '%d' % req.task_id
        logging.debug("Push WSP request (id=%s, url=%s) into the topic %s" % (req.id, req.url, topic))
        tempreq = pickle.dumps(req)
        self.producer.send(topic, tempreq)

    def _pull_req(self):
        while self.isRunning:
            with self._task_lock:
                no_work = not self.taskDict
            if no_work:
                # FIXME: 这里暂定休息5s
                sleep_time = 5
                logging.debug("No work, and I will sleep %s seconds" % sleep_time)
                time.sleep(sleep_time)
            else:
                record = next(self.consumer)
                req = pickle.loads(record)
                logging.debug("The WSP request (id=%s, url=%s) has been pulled" % (req.id, req.url))
                self._push_task(req)

    def _start_pull_req(self):
        logging.info("Start to pull requests")
        t = threading.Thread(target=self._pull_req)
        t.start()

    @_convert_request
    def _push_task(self, req):
        while True:
            if self.downloader.add_task(req, self.saveResult):
                break
            # FIXME: 这里暂定休息1s
            sleep_time = 1
            logging.debug("Downloader is busy, and I will sleep %s seconds" % sleep_time)
            time.sleep(sleep_time)

    @_convert_result
    def saveResult(self, req, response):
        response.id = ObjectId()
        response.req_id = req.id
        response.task_id = req.task_id
        logging.debug("Save the WSP request (id=%s, url=%s)" % (req.id, req.url))
        logging.debug("Save the WSP response (id=%s, url=%s, http_code=%s, error=%s)" % (response.id, response.url, response.http_code, response.error))
        reqTable = self.db.request
        reqJason = {
            'id':req.id,
            'father_id':req.father_id,
            'task_id':req.task_id,
            'url':req.url,
            'level':req.level,
            'retry':req.retry,
            'proxy':req.proxy,
            'fetcher':req.fetcher
        }
        reqTable.save(reqJason)
        respTable = self.db.response
        respJason = {
            'id':response.id,
            'req_id':response.req_id,
            'task_id':response.task_id,
            'url':response.url,
            'html':response.html,
            'http_code':response.http_code,
            'error':response.error
        }
        respTable.save(respJason)
        tid = '%d'%req.task_id
        resTable = self.db['result_'+tid]
        resTable.save({'id':ObjectId(),'req':reqJason,'resp':respJason})
        if response.error is not None:
            req.retry += 1
            if req.retry < self.taskDict[req.task_id].max_retry:
                self.pushReq(req)
            else:
                logging.debug("The WSP request(id=%s, url=%s) has been retried %d times, and it will be aborted." % (req.id, req.url, req.retry))
        else:
            url_list = re.findall(r'<a[\s]*href[\s]*=[\s]*["|\']?(.*?)["|\']?>', response.html)
            hasNewUrl = False
            for u in url_list:
                if u.startswith('//'):
                    if req.url.startswith("http:"):
                        u = 'http:' + u
                    else:
                        u = 'https:' + u
                elif not u.startswith('http://') and not u.startswith("https://"):
                    strlist = req.url.split('?')
                    u = strlist[0] + u
                else:
                    followDict = self.taskDict[req.task_id].follow
                    tag = False
                    for rule in followDict['starts_with']:
                        if u.startswith(rule):
                            tag = True
                            break
                    if not tag:
                        for rule in followDict['ends_with']:
                            if u.endswith(rule):
                                tag = True
                                break
                    if not tag:
                        for rule in followDict['contains']:
                            if u.__contains__(rule):
                                tag = True
                                break
                    if not tag:
                        for rule in followDict['regex_matches']:
                            if re.search(rule, u):
                                tag = True
                                break
                    if tag:
                        logging.debug("Find a new url %s in the page %s." % (u, req.url))
                        hasNewUrl = True
                        newReq = WspRequest()
                        newReq.id = ObjectId()
                        newReq.father_id = req.id
                        newReq.task_id = req.task_id
                        newReq.url = u
                        newReq.level=req.level+1
                        self.pushReq(req)
            if hasNewUrl:
                self.producer.flush()
