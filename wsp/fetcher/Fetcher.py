import pickle
import time
import re
from pymongo import MongoClient
from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer
from bson.objectid import ObjectId
from kafka import KafkaProducer
from kafka import KafkaConsumer
from aiohttp.client_reqrep import helpers

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
    def __init__(self, server_addr, downloader_clients, kafka_addr,mongo_host,mongo_port):
        self.isRunning = True
        self.rpcServer = SimpleXMLRPCServer(server_addr, allow_none=True)
        self.rpcServer.register_function(self.changeTasks)
        self.rpcServer.register_function(self.pullReq)
        # self.rpcServer.serve_forever()
        # 开启RPC服务
        self.start_rpc_server()
        client = MongoClient(mongo_host,mongo_port)
        self.db = client.wsp
        self.producer = KafkaProducer(bootstrap_servers=[kafka_addr,])
        self.consumer = KafkaConsumer(bootstrap_servers=[kafka_addr,], auto_offset_reset='earliest')
        self.downloader = Downloader(clients=downloader_clients)
        self.taskDict = {}

    def start_rpc_server(self):
        t = Thread(target=self.rpcServer.serve_forever)
        t.start()

    def changeTasks(self, tasks):
        topics = []
        for t in tasks:
            topic = '%d' % t.id
            topics.append(topic)
        self.consumer.subscribe(topics)
        self.taskDict = {}
        for t in tasks:
            self.taskDict[t.id] = t

    def pushReq(self, req):
        topic = '%d' % req.task_id
        tempreq = pickle.dumps(req)
        self.producer.send(topic, tempreq)

    def pullReq(self):
        while self.isRunning:
            if not self.taskDict:
                record = next(self.consumer)
                req = pickle.loads(record)
                self._push_task(req)
            else:
                time.sleep(5)

    @_convert_request
    def _push_task(self, req):
        while True:
            if self.downloader.add_task(req, self.saveResult):
                break
            # TODO: 这里暂定写死休息1s，回头再修改
            time.sleep(1)

    @_convert_result
    def saveResult(self, req, response):
        response.id = ObjectId()
        response.req_id = req.id
        response.task_id = req.task_id
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
                        hasNewUrl = True
                        newReq = WspRequest()
                        newReq.id = ObjectId()
                        newReq.father_id = req.id
                        newReq.task_id = req.task_id
                        newReq.url = u
                        newReq.level+=1
                        self.pushReq(req)
            if hasNewUrl:
                self.producer.flush()
