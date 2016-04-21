# coding=utf-8

import time
import json
import re

from bson import ObjectId
import pymysql
from pymongo import MongoClient
from kafka.producer import KafkaProducer

from wsp.utils.parse import text_from_http_body
from wsp.errors import ResponseNotMatch


class StoreMiddleware:

    mongo_addr = "mongodb://wsp:wsp123456@192.168.120.90:27017"
    mongo_db = "ScholarInfoBase"
    mongo_tbl = "wanfang"
    mysql_host = "192.168.120.90"
    mysql_user = "root"
    mysql_pwd = "123456"
    kafka_addr = "192.168.120.90:9092"
    kafka_topic = "wanfang"

    def __init__(self):
        self._mongo_client = MongoClient(self.mongo_addr)
        self._tbl = self._mongo_client[self.mongo_db][self.mongo_tbl]
        self._conn = pymysql.connect(host=self.mysql_host,
                                     user=self.mysql_user,
                                     password=self.mysql_pwd,
                                     db="ScholarInfoBase")
        self._producer = KafkaProducer(bootstrap_servers=[self.kafka_addr, ])
        self._id_match = re.compile(r"d\.wanfangdata\.com\.cn(.*?)$")

    async def handle_input(self, response):
        # print("Response url: %s" % response.url)
        url = response.url
        if url.find("d.wanfangdata.com.cn") >= 0:
            self._store(response)

    def _store(self, response):
        url = response.url
        obj_id = ObjectId()
        sql = "insert into `WanfangMetaSource` (ID, detailPageId, detailPageUrl, crawlTime) values (%s, %s, %s, %s)"
        page_id = "%s" % obj_id
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        id = None
        for i in self._id_match.findall(url):
            id = i
            break
        if id:
            try:
                html = text_from_http_body(response)
                self._conn.ping(True)
                with self._conn.cursor() as cursor:
                    cursor.execute(sql, (id, page_id, url, t))
                self._tbl.insert_one({"_id": obj_id, "url": url, "body": response.body})
                data_dict = {"id": id, "crawl_time": t, "html": html}
                self._producer.send(self.kafka_topic, json.dumps(data_dict).encode("utf-8"))
            except pymysql.IntegrityError:
                pass
            except UnicodeDecodeError as e:
                raise ResponseNotMatch("%s" % e)
