# coding=utf-8

DEFAULT_RPC_ADDR = "0.0.0.0:7310"
DEFAULT_MONITOR_ADDR = "0.0.0.0:7311"


class MasterConfig:

    def __init__(self, **kw):
        self.rpc_addr = kw.get("rpc_addr", DEFAULT_RPC_ADDR)
        self.monitor_addr = kw.get("monitor_addr", DEFAULT_MONITOR_ADDR)
