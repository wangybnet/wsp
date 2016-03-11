# encoding: utf-8


from pymongo import MongoClient
from wsp.fetcher.fetcherManager import fetcherManager



class Master(object):

    def __init__(self):
        self.fetcher_manager = fetcherManager()

    #建立mongodb连接并选择集合
    def __get_col(self, db_name, col_name):
        client = MongoClient()
        collection = client[db_name][col_name]
        return collection

    def create_one(self, task):
        collection = self.__get_col('wsp', 'task')
        task_id = collection.insert_one(task).inserted_id #返回任务ID
        return task_id

    def delete_one(self, task_id):
        collection = self.__get_col('wsp', 'task')
        flag = collection.remove({'_id' : task_id})
        return flag

    def start_one(self, task_id):
        collection = self.__get_col('wsp', 'task')
        task = collection.find_one({'_id' : task_id})
        tasks = []
        tasks.append(task)
        flag = self.fetcher_manager.start(tasks)
        if flag:
            print('任务已经启动')
        else:
            print('任务启动失败')




    def stop_one(self, task_id):
        collection = self.__get_col('wsp', 'task')
        task = collection.find_one({'_id' : task_id})
        return task






