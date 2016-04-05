# coding:utf-8

import unittest
from pymongo import MongoClient
#from wsp.master.master import Master
import xmlrpc.client

global inserted_id
global flag

class TestMaster(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.task = {"test" : "test_create"}
        print("开始测试")

    def test_create_one(self):
        master = Master()
        global inserted_id
        inserted_id = master.create_task(self.task)
        self.assertIsNotNone(inserted_id)

    def test_start_one(self):
        master = Master()
        global inserted_id
        master.start_task(inserted_id)

    @classmethod
    def tearDownClass(self):
        master = Master()
        global inserted_id
        global flag
        print(inserted_id)
        flag = master.delete_task(inserted_id)
        print("测试结束")

    def test_get_argu(self):
        s = xmlrpc.client.ServerProxy('http://127.0.0.1:8090')
        print(s.get_argu())


if __name__ == '__main__':
    unittest.main()
