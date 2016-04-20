# coding=utf-8

import time
import json

from bson import ObjectId
import pymysql
from pymongo import MongoClient
from kafka.producer import KafkaProducer

from wsp.utils.parse import text_from_http_body
from wsp.errors import ResponseNotMatch


class StoreMiddleware:

    match_url = "dl.acm.org/citation.cfm"
    mongo_addr = "mongodb://wsp:wsp123456@192.168.120.90:27017"
    mongo_db = "ScholarInfoBase"
    mongo_collection = "acm"
    mysql_host = "192.168.120.90"
    mysql_user = "root"
    mysql_pwd = "123456"
    kafka_addr = "192.168.120.90:9092"
    kafka_topic = "acm"
    not_found_feature = """<div class="medium-text">Unknown Item</div>"""

    def __init__(self):
        self._mongo_client = MongoClient(self.mongo_addr)
        self._coll = self._mongo_client[self.mongo_db][self.mongo_collection]
        self._conn = pymysql.connect(host=self.mysql_host,
                                     user=self.mysql_user,
                                     password=self.mysql_pwd,
                                     db="ScholarInfoBase")
        self._producer = KafkaProducer(bootstrap_servers=[self.kafka_addr, ])

    async def handle_input(self, response):
        # print("%s Response url: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), response.url))
        if response.url.find(self.match_url) >= 0:
            self._store(response)

    def _store(self, response):
        url = response.request.url
        obj_id = ObjectId()
        sql = "insert into `ACMMetaSource` (ID, detailPageId, detailPageUrl, crawlTime) values (%s, %s, %s, %s)"
        page_id = "%s" % obj_id
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        eq = url.rindex("=")
        id = url[eq + 1:]
        try:
            html = text_from_http_body(response)
            if html.find(self.not_found_feature) >= 0:
                return
            self._conn.ping(True)
            with self._conn.cursor() as cursor:
                cursor.execute(sql, (id, page_id, url, t))
            self._coll.insert_one({"_id": obj_id, "url": url, "body": response.body})
            data_dict = {"id": id, "crawl_time": t, "html": html}
            self._producer.send(self.kafka_topic, json.dumps(data_dict).encode("utf-8"))
        except pymysql.IntegrityError:
            pass
        except UnicodeDecodeError as e:
            raise ResponseNotMatch("%s" % e)
