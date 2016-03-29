# coding=utf-8

DEFAULT_RPC_ADDR = "0.0.0.0:8091"


class MasterConfig:

    def __init__(self, **kw):
        self.rpc_addr = kw.get("rpc_addr", DEFAULT_RPC_ADDR)
        self.sys_kafka_addr = kw.get("sys_kafka_addr", None)
        self.sys_mongo_addr = kw.get("sys_mongo_addr", None)
        self.sys_agent_addr = kw.get("sys_agent_addr", None)
