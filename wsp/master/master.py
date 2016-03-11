# encoding: utf-8


from pymongo import MongoClient



class Master(object):

    #建立mongodb连接并选择集合
    def __get_col(self, db_name, col_name):
        client = MongoClient()
        collection = client[db_name][col_name]
        return collection

    def create(self, task):
        collection = self.__get_col('wsp', 'task')
        task_id = collection.insert_one(task).inserted_id #返回任务ID
        return task_id

    def delete(self, task_id):
        collection = self.__get_col('wsp', 'task')
        flag = collection.remove({'_id' : task_id})
        return flag











