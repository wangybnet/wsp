# coding=utf-8

import pickle
from xmlrpc.client import ServerProxy

from kafka import KafkaProducer
from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.fetcher.request import WspRequest


class fetcherManager:

    def __init__(self, kafka_addr, mongo_addr):
        mongo_host, mongo_port = mongo_addr.split(":")
        mongo_port = int(mongo_port)
        self.running_tasks = []
        self.fetcherList = []
        self.producer = KafkaProducer(bootstrap_servers=[kafka_addr, ])
        client = MongoClient(mongo_host, mongo_port)
        db = client.wsp
        self.taskTable = db.tasks

    def add_fetcher(self, fetcher_addr):
        if fetcher_addr not in self.fetcherList:
            self.fetcherList.append(fetcher_addr)

    def _start(self):
        for f in self.fetcherList:
            if not f.startswith("http://"):
                f = "http://" + f
            rpcClient = ServerProxy(f, allow_none=True)
            rpcClient.changeTasks(self.running_tasks)
        # FIXME: 默认返回True 之后可能根据rpc连接情况修改
        return True

    def delete(self,tasks):
        # TODO: 从kafka中删除topic
        for t in tasks:
            self.taskTable.update({"id":t.id},{"$set":{'status':3}})
            self.running_tasks.remove(t)
        return self._start()

    def stop(self,tasks):
        for t in tasks:
            self.taskTable.update({"id":t.id},{"$set":{'status':2}})
            self.running_tasks.remove(t)
        return self._start()

    def start(self,tasks):
        for t in tasks:
            if t.status==0:
                for url in t.start_urls:
                    obj_id = ObjectId()
                    req = WspRequest(id=obj_id,
                                     father_id=obj_id,
                                     task_id=t.id,
                                     url=url)
                    self._pushReq(req)
                self.producer.flush()
            self.taskTable.update({"id":t.id},{"$set":{'status':1}})
            if t not in self.running_tasks:
                self.running_tasks.append(t)
        return self._start()

    def _pushReq(self, req):
        topic = '%d' % req.task_id
        tempreq = pickle.dumps(req)
        self.producer.send(topic, tempreq)
