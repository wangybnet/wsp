# coding=utf-8


class WspConfig:

    def __init__(self, **kw):
        self.kafka_addr = kw.get("kafka_addr", None)
        self.mongo_addr = kw.get("mongo_addr", None)
        self.agent_addr = kw.get("agent_addr", None)
