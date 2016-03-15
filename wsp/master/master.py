# encoding: utf-8

from pymongo import MongoClient
from wsp.fetcher.fetcherManager import fetcherManager
from xmlrpc.server import SimpleXMLRPCServer
from wsp.master.deal_yaml import DealYaml


class Master(object):

    def __init__(self):
        self.fetcher_manager = fetcherManager()
        self.deal_yaml = DealYaml()

    '''
    Master类的功能:
        [1].新建任务,任务建立成功返回任务ID
        [2].删除任务,删除成功返回true
        [3].启动单个任务,启动成功返回true
        [4].停止单个任务,停止成功返回true
        [5].返回配置文件信息供fetcher使用
    '''

    def __init__(self):
        #self.fetcher_manager = fetcherManager()
        self.deal_yaml = DealYaml()

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

    # 供fetchers获取参数的接口
    def get_argu(self):
        self.deal_yaml = DealYaml()
        self.filename = "../../release/etc/master.yaml"
        return self.deal_yaml.yaml_to_dict(self.filename)


sxr = SimpleXMLRPCServer(("127.0.0.1", 8090))
sxr.register_instance(Master())
sxr.serve_forever()
