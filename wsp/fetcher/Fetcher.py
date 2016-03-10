import pickle
import time
import re
import pymongo
from bson.objectid import ObjectId
from kafka import KafkaProducer
from kafka import KafkaConsumer

from wsp.downloader import Downloader
from wsp.fetcher.request import WspRequest


class Fetcher:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')
        self.consumer = KafkaConsumer(bootstrap_servers='localhost:9092', auto_offset_reset='earliest')
        self.downloader = Downloader()
        self.taskDict = {}
        self.count = 0

    def changeTasks(self, tasks):
        topics = []
        for t in tasks:
            topic = '%d' % t.id
            topics.append(topic)
            if t.id not in self.taskDict.keys():
                t.status = 1
                for url in t.start_urls:
                    req = WspRequest()
                    req.id = ObjectId()
                    req.father_id = req.id
                    req.task_id = t.id
                    self.pushReq(req)
                self.producer.flush()
        self.consumer.subscribe(topics)
        for t in self.taskDict.values():
            if t not in tasks:
                t.status = 2
        self.taskDict = {}
        for t in tasks:
            self.taskDict[t.id] = t

    def pushReq(self, req):
        topic = '%d' % req.task_id
        fileObj = open("G:\Reqfile.txt", 'w')
        pickle.dump(req, fileObj, 0)
        fileObj.close()
        fileObj = open("G:\Reqfile.txt", 'r')
        allText = fileObj.read()
        fileObj.truncate()
        fileObj.close()
        bytes(allText, encoding="utf8")
        self.producer.send(topic, allText)

    def pullReq(self, ):
        for record in self.consumer:
            fileObj = open("G:\Reqfile.txt", 'w')
            fileObj.write(record.value)
            fileObj.close()
            fileObj = open("G:\Reqfile.txt", 'r')
            req = pickle.load(fileObj)
            fileObj.close()
            self.count += 1
            if (self.count == 200):
                time.sleep(5)

    # TODO: @GladysLau 请通过调用self._push_task(req)这个函数给downloader传递任务，参数req是WspRequest。By the way, 看到此消息后请删除这行。
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
        conn = pymongo.Connection('localhost',27017)
        db = conn.wsp
        reqTable = db.request
        reqJason = {'id':req.id,'father_id':req.father_id,'task_id':req.task_id,'url':req.url,'level':req.level,'retry':req.retry,'proxy':req.proxy,'fetcher':req.fetcher}
        reqTable.save(reqJason)
        respTable = db.response
        respJason = {'id':response.id,'req_id':response.req_id,'task_id':response.task_id,'url':response.url,'html':response.html,'http_code':response.http_code,'error':response.error}
        respTable.save(respJason)
        tid = '%d'%req.task_id
        resTable = db['result_'+tid]
        resTable.save({'id':ObjectId(),'req':reqJason,'resp':respJason})
        if response.error != None:
            req.retry += 1
            self.pushReq(req)
        else:
            url_list = re.findall(r'<a[\s]*href[\s]*=[\s]*"(.*?)">', response.html)
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
                    newReq = WspRequest()
                    newReq.id = ObjectId()
                    newReq.father_id = req.id
                    newReq.task_id = req.task_id
                    newReq.url = u
                    newReq.level+=1
                    self.pushReq(req)
            self.producer.flush()


# 将WSP的request转换成Downloader的request
def _convert_request(func):
    def wrapper(req):
        # TODO @wangybnet 添加代码

        return func(req)
    return wrapper


# 将Downloader的request和reponse转换成WSP的request和response
def _convert_result(func):
    def wrapper(req, resp):
        # TODO @wangybnet 添加代码

        return func(req, resp)
    return wrapper

