# coding=utf-8

import time
import datetime

from bson import ObjectId
import pymysql
from pymongo import MongoClient


class StoreMiddleware:

    match_url = "d.wanfangdata.com.cn"
    mongo_addr = "mongodb://wsp:wsp123456@192.168.120.90:27017"
    mongo_db = "ScholarInfoBase"
    mongo_collection = "WanfangMetaSource"
    mysql_host = "192.168.120.90"
    mysql_user = "root"
    mysql_pwd = "123456"

    def __init__(self):
        self._mongo_client = MongoClient(self.mongo_addr)
        self._coll = self._mongo_client[self.mongo_db][self.mongo_collection]
        self._conn = pymysql.connect(host=self.mysql_host,
                                     user=self.mysql_user,
                                     password=self.mysql_pwd,
                                     db="ScholarInfoBase")
        self._cur = self._conn.cursor()

    async def handle_input(self, response):
        print("Response url: %s" % response.url)
        if response.url.find(self.match_url) >= 0:
            self._store(response)

    def _store(self, response):
        url = response.url
        obj_id = ObjectId()
        sql = "insert into `WanfangMetaSource` (ID, detailPageId, detailPageUrl, crawlTime) values (%s, %s, %s, %s)"
        page_id = "%s" % obj_id
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            slash = url.index("/")
            id = url[slash:]
        except Exception:
            pass
        else:
            self._coll.insert_one({"_id": obj_id, "url": url, "body": response.body})
            self._cur.execute(sql, (id, page_id, url, t))
