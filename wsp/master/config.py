# coding=utf-8

DEFAULT_RPC_ADDR = "0.0.0.0:8091"


class MasterConfig:

    def __init__(self, **kw):
        self.rpc_addr = kw.get("rpc_addr", DEFAULT_RPC_ADDR)
