# encoding: utf-8

from xmlrpc.server import SimpleXMLRPCServer
from pymongo import MongoClient
from wsp.fetcher.fetcherManager import fetcherManager



class Master(object):


    '''
    Master类的功能:
        [1].新建任务,任务建立成功返回任务ID
        [2].删除任务,删除成功返回true
        [3].启动单个任务,启动成功返回true
        [4].停止单个任务,停止成功返回true
        [5].返回配置文件信息供fetcher使用
    '''

    def __init__(self, config):
        self.config = config

        # self.fetcher_manager = fetcherManager(
        #     self.config['fetchers'],
        #     self.config['kafka_addr'],
        #     self.self.config['mongo_host'],
        #     self.config['mongo_port']
        # )

    # 建立mongodb连接并选择集合
    def __get_col(self, db_name, col_name):
        client = MongoClient()
        collection = client[db_name][col_name]
        return collection

    def create_one(self, task):
        collection = self.__get_col('wsp', 'task')
        task_id = collection.insert_one(task).inserted_id  # 返回任务ID
        return task_id

    def delete_one(self, task_id):
        collection = self.__get_col('wsp', 'task')
        flag = collection.remove({'_id': task_id})
        return flag

    def start_one(self, task_id):
        collection = self.__get_col('wsp', 'task')
        task = collection.find_one({'_id': task_id})
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.start(tasks)
        return flag

    def stop_one(self, task_id):
        collection = self.__get_col('wsp', 'task')
        task = collection.find_one({'_id': task_id})
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.stop(tasks)
        return flag

    def get_config(self):
        return self.config

    def start(self):
        print("start")
        sxr = SimpleXMLRPCServer(("0.0.0.0", 8090), allow_none=True)
        # sxr.register_instance(self)
        sxr.register_function(self.get_config)
        sxr.serve_forever()