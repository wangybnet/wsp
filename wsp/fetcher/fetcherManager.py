# coding=utf-8

import logging
import pickle
from xmlrpc.client import ServerProxy

from kafka import KafkaProducer
from pymongo import MongoClient
from bson.objectid import ObjectId

from wsp.fetcher.request import WspRequest


class fetcherManager:

    def __init__(self, kafka_addr, mongo_addr):
        logging.debug("New fetcher manager with kafka_addr=%s, mongo_addr=%s" % (kafka_addr, mongo_addr))
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
            logging.debug("Add a new fetcher %s" % fetcher_addr)
            self.fetcherList.append(fetcher_addr)

    def _start(self):
        logging.debug("Change the tasks of the fetchers %s" % self.fetcherList)
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
            logging.debug("Delete task %s (status=%s)" % (t.id, t.status))
            self.taskTable.update({"id":t.id},{"$set":{'status':3}})
            self.running_tasks.remove(t)
        return self._start()

    def stop(self,tasks):
        for t in tasks:
            logging.debug("Stop task %s (status=%s)" % (t.id, t.status))
            self.taskTable.update({"id":t.id},{"$set":{'status':2}})
            self.running_tasks.remove(t)
        return self._start()

    def start(self,tasks):
        for t in tasks:
            logging.debug("Start task %s (status=%s)" % (t.id, t.status))
            if t.status==0:
                logging.debug("Push the start URLs %s of task %s" % (t.start_urls, t.id))
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
        topic = '%s' % req.task_id
        logging.debug("Push WSP request (id=%s, url=%s) into the topic %s" % (req.id, req.url, topic))
        tempreq = pickle.dumps(req)
        self.producer.send(topic, tempreq)
