# coding=utf-8

from xmlrpc.client import ServerProxy


class fetcherManager:

    def __init__(self,flist):
        self.cur_tasks = []
        self.fetcherList = flist

    def start(self,tasks):
        for t in tasks:
            self.cur_tasks.append(t)
        for f in self.fetcherList:
            rpcClient = ServerProxy(f)
            rpcClient.changeTasks(self.cur_tasks)
        # TODO:默认返回True 之后可能根据rpc连接情况修改
        return True

    def stop(self,tasks):
        for t in tasks:
            self.cur_tasks.remove(t)
        for f in self.fetcherList:
            rpcClient = ServerProxy(f)
            rpcClient.changeTasks(self.cur_tasks)
        # TODO:默认返回True 之后可能根据rpc连接情况修改
        return True
