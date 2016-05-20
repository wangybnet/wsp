# coding=utf-8

from queue import Queue


class Agent:

    def __init__(self, agent_config):
        self._proxy_queue = Queue()
        self._backup_queue = Queue()

    def start(self):
        self._start_agent_server()
        self._start_agent_spider()

    def _start_agent_server(self):
        pass

    def _start_agent_spider(self):
        pass
