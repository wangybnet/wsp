from kafka import KafkaProducer
from kafka import KafkaConsumer
from Downloader import Downloader
from Request import WSPrequest
from Response import WSPresponse
import pymongo
import pickle
import time
import re

class Fetcher:

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        self.consumer = KafkaConsumer(bootstrap_servers='localhost:9092',auto_offset_reset='earliest')
        self.downloader = Downloader()
        self.taskDict = {}
        self.count = 0

    def changeTasks(self,tasks):
        topics = []
        for t in tasks:
            topic = '%d'%t.id
            topics.append(topic)
            if t.id not in taskDict.keys():
                for url in t.start_urls:
                    req = WSPrequest()
                    req.id = ObjectId()
                    req.father_id = req.id
                    req.task_id = t.id
                    self.pushReq(req)
                self.producer.flush()
        self.consumer.subscribe(topics)
        self.taskDict = {}
        for t in tasks:
            self.taskDict[t.id] = t

    def pushReq(self,req):
        topic = '%d'%req.task_id
        fileObj = open("/home/samba/reqfile.txt",'w')
        pickle.dump(req,fileObj,0)
        fileObj.close()
        fileObj = open("/home/samba/reqfile.txt",'r')
        allText = fileObj.read()
        fileObj.truncate()
        fileObj.close()
        bytes(allText, encoding = "utf8")
        self.producer.send(topic,allText)

    def pullReq(self,):
        for record in consumer:
            fileObj = open("/home/samba/reqfile.txt",'w')
            fileObj.write(record.value)
            fileObj.close()
            fileObj = open("/home/samba/reqfile.txt",'r')
            req = pickle.load(fileObj)
            fileObj.close()
            self.downloader.download()
            ++count
            if(count==200)
                time.sleep(5)

    def saveResult(self,req,response):
        res = WSPresponse()
        res.id = ObjectId()
        res.req_id = req.id
        res.task_id = req.task_id
        res.url = req.url
        res.html = response.html 
        pass
        



