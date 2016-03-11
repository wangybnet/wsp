import xmlrpc.client

class fetcherManager:

    def __init__(self,flist):
        self.cur_tasks = []
        self.fetcherList = flist

    def start(self,tasks):
        for t in tasks:
            self.cur_tasks.append(t)
        for f in self.fetcherList:
            rpcClient = xmlrpc.client.ServerProxy(f)
            rpcClient.changeTasks(self.cur_tasks)

    def stop(self,tasks):
        for t in tasks:
            self.cur_tasks.remove(t)
        for f in self.fetcherList:
            rpcClient = xmlrpc.client.ServerProxy(f)
            rpcClient.changeTasks(self.cur_tasks)
