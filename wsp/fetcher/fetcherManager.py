# coding=utf-8

from kafka import KafkaProducer
from xmlrpc.client import ServerProxy
from wsp.fetcher.request import WspRequest

import pymongo
from bson.objectid import ObjectId


class fetcherManager:

    def __init__(self,flist,kafka_addr):
        self.running_tasks = []
        self.fetcherList = flist
        self.producer = KafkaProducer(bootstrap_servers=[kafka_addr,])
        conn = pymongo.Connection('localhost',27017)
        db = conn.wsp
        self.taskTable = db.tasks

    def _start(self):
        for f in self.fetcherList:
            rpcClient = ServerProxy(f)
            rpcClient.changeTasks(self.running_tasks)
        # TODO:默认返回True 之后可能根据rpc连接情况修改
        return True

    def delete(self,tasks):
        # TODO: 从kafka中删除任务
        for t in tasks:
            self.taskTable.update({"id":t.id},{"$set":{'status':3}})
            self.runing_tasks.remove(t)
        return self._start()

    def stop(self,tasks):
        for t in tasks:
            self.taskTable.update({"id":t.id},{"$set":{'status':2}})
            self.runing_tasks.remove(t)
        return self._start()

    def start(self,tasks):
        for t in tasks:
            if t.status==0:
                for url in t.start_urls:
                    req = WspRequest()
                    req.id = ObjectId()
                    req.father_id = req.id
                    req.task_id = t.id
                    self.pushReq(req)
                self.producer.flush()
            self.taskTable.update({"id":t.id},{"$set":{'status':1}})
            self.running_tasks.append(t)
        return self._start()








